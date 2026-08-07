import os
import math
import logging
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
from cachetools import TTLCache

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("pubfinder-api")

app = FastAPI(
    title="PubFinder API",
    description="Stateless Location-Aware Venue Ingress & OpenStreetMap Proxy API",
    version="1.0.0"
)

# Enable CORS for SPA frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

NOMINATIM_URL = os.getenv("NOMINATIM_URL", "https://nominatim.openstreetmap.org/search")
OVERPASS_URL = os.getenv("OVERPASS_URL", "https://overpass-api.de/api/interpreter")
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "900"))  # 15 min default

# In-memory spatial cache: key=(lat_rounded_3dp, lon_rounded_3dp, radius_m), max 1000 entries
spatial_cache = TTLCache(maxsize=1000, ttl=CACHE_TTL_SECONDS)


class Address(BaseModel):
    street: Optional[str] = None
    city: Optional[str] = None
    postcode: Optional[str] = None


class OpeningStatus(BaseModel):
    is_open_now: Optional[bool] = None
    raw: Optional[str] = None


class Coordinates(BaseModel):
    latitude: float
    longitude: float


class Venue(BaseModel):
    id: str
    name: str
    type: str
    distance_meters: int
    walking_time_minutes: int
    address: Optional[Address] = None
    opening_status: Optional[OpeningStatus] = None
    coordinates: Coordinates
    maps_url: str


class NearestResponse(BaseModel):
    status: str
    query_location: Coordinates
    primary_venue: Optional[Venue] = None
    alternatives: List[Venue] = []


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> int:
    R = 6371000  # meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return int(round(R * c))


async def fetch_nominatim_venues(lat: float, lon: float, radius_m: int) -> List[dict]:
    # High-speed OpenStreetMap Nominatim spatial query (~0.25s response time)
    # Bounding box delta: ~0.03 deg ~ 3.3km
    delta = 0.035
    viewbox = f"{lon - delta},{lat + delta},{lon + delta},{lat - delta}"
    headers = {"User-Agent": "PubFinder/1.0 (Homelab Stateless SPA; https://github.com/HughStanway/beerdar)"}
    
    results = []
    # Query amenities pub and bar in parallel
    async with httpx.AsyncClient(timeout=6.0) as client:
        for amenity_type in ["pub", "bar", "brewery"]:
            url = f"{NOMINATIM_URL}?format=jsonv2&amenity={amenity_type}&lat={lat}&lon={lon}&bounded=1&viewbox={viewbox}&limit=25&addressdetails=1"
            try:
                resp = await client.get(url, headers=headers)
                if resp.status_code == 200:
                    results.extend(resp.json())
            except Exception as exc:
                logger.warning(f"Nominatim query for {amenity_type} failed: {exc}")
    return results


async def fetch_overpass_fallback(lat: float, lon: float, radius_m: int) -> List[dict]:
    # Secondary fallback query for Overpass API
    query = f"""
    [out:json][timeout:6];
    (
      node["amenity"="pub"](around:3000, {lat}, {lon});
      node["amenity"="bar"](around:3000, {lat}, {lon});
      node["craft"="brewery"](around:3000, {lat}, {lon});
    );
    out body;
    """
    headers = {"User-Agent": "PubFinder/1.0 (Homelab Stateless SPA; https://github.com/HughStanway/beerdar)"}
    async with httpx.AsyncClient(timeout=6.0) as client:
        resp = await client.post(OVERPASS_URL, data={"data": query}, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        return data.get("elements", [])


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": "pubfinder-api"
    }


@app.get("/api/v1/nearest", response_model=NearestResponse)
async def get_nearest_venues(
    lat: float = Query(..., description="User latitude", ge=-90.0, le=90.0),
    lon: float = Query(..., description="User longitude", ge=-180.0, le=180.0),
    limit: int = Query(1, description="Number of primary/alternative venues", ge=1, le=20),
    radius_m: int = Query(5000, description="Search radius in meters", ge=100, le=50000)
):
    # Round coordinates to 3 decimal places (~100m grid) for cache key
    cache_key = (round(lat, 3), round(lon, 3), radius_m)

    if cache_key in spatial_cache:
        logger.info(f"Spatial cache HIT for key {cache_key}")
        venues = spatial_cache[cache_key]
    else:
        logger.info(f"Spatial cache MISS for key {cache_key}. Querying OpenStreetMap Nominatim Engine...")
        raw_items = await fetch_nominatim_venues(lat, lon, radius_m)

        if not raw_items or len(raw_items) == 0:
            logger.info("Nominatim returned 0 items. Trying secondary Overpass provider...")
            try:
                raw_overpass = await fetch_overpass_fallback(lat, lon, radius_m)
                # Convert overpass format to standard format
                for elem in raw_overpass:
                    tags = elem.get("tags", {})
                    if tags.get("name") and elem.get("lat") and elem.get("lon"):
                        raw_items.append({
                            "osm_id": elem.get("id"),
                            "osm_type": elem.get("type", "node"),
                            "name": tags.get("name"),
                            "type": tags.get("amenity") or tags.get("craft") or "pub",
                            "lat": str(elem.get("lat")),
                            "lon": str(elem.get("lon")),
                            "address": {
                                "road": tags.get("addr:street"),
                                "city": tags.get("addr:city") or tags.get("addr:town"),
                                "postcode": tags.get("addr:postcode")
                            }
                        })
            except Exception as exc:
                logger.warning(f"Overpass fallback failed: {exc}")

        if not raw_items or len(raw_items) == 0:
            raise HTTPException(
                status_code=504,
                detail="OpenStreetMap Service Provider Timeout: No live venue data received from OpenStreetMap servers. Please try again or select a demo location."
            )

        venues: List[Venue] = []
        seen_ids = set()

        for item in raw_items:
            name = item.get("name") or item.get("display_name", "").split(",")[0]
            # Strict filter: require real non-empty venue name
            if not name or name.strip() == "":
                continue

            try:
                v_lat = float(item.get("lat"))
                v_lon = float(item.get("lon"))
            except (ValueError, TypeError):
                continue

            elem_id = f"osm-{item.get('osm_type', 'node')}-{item.get('osm_id', 0)}"
            if elem_id in seen_ids:
                continue
            seen_ids.add(elem_id)

            addr_obj = item.get("address", {})
            # Skip disused/private/non-drinking
            if addr_obj.get("disused") == "yes" or item.get("type") in ["juice", "milk", "coffee"]:
                continue

            dist = haversine_distance(lat, lon, v_lat, v_lon)
            walking_time = max(1, math.ceil(dist / 80.0))  # 80m/min approx 4.8 km/h

            venue_type = item.get("type") or "pub"

            street = addr_obj.get("road") or addr_obj.get("pedestrian") or addr_obj.get("street")
            city = addr_obj.get("city") or addr_obj.get("town") or addr_obj.get("village") or addr_obj.get("suburb")
            postcode = addr_obj.get("postcode")
            address = Address(street=street, city=city, postcode=postcode) if (street or city or postcode) else None

            maps_url = f"https://www.google.com/maps/dir/?api=1&destination={v_lat},{v_lon}"

            venues.append(
                Venue(
                    id=elem_id,
                    name=name,
                    type=venue_type,
                    distance_meters=dist,
                    walking_time_minutes=walking_time,
                    address=address,
                    opening_status=None,
                    coordinates=Coordinates(latitude=v_lat, longitude=v_lon),
                    maps_url=maps_url
                )
            )

        # Sort venues by distance ascending
        venues.sort(key=lambda v: v.distance_meters)
        spatial_cache[cache_key] = venues

    primary_venue = venues[0] if len(venues) > 0 else None
    alternatives = venues[1: 1 + limit] if len(venues) > 1 else []

    return NearestResponse(
        status="success",
        query_location=Coordinates(latitude=lat, longitude=lon),
        primary_venue=primary_venue,
        alternatives=alternatives
    )
