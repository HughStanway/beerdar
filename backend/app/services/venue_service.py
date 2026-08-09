import logging

from fastapi import HTTPException

from app.cache.base import BaseCacheRepository, SpatialCacheKey
from app.providers.base import BaseGeospatialProvider, RawVenueData
from app.schemas.address import Address
from app.schemas.coordinates import Coordinates
from app.schemas.opening_status import OpeningStatus
from app.schemas.response import NearestResponse
from app.schemas.venue import Venue
from app.services.geo import GeoService

logger = logging.getLogger(__name__)


class VenueService:
    def __init__(
        self,
        provider: BaseGeospatialProvider,
        cache: BaseCacheRepository,
        geo_service: GeoService | None = None,
    ):
        self._provider = provider
        self._cache = cache
        self._geo_service = geo_service or GeoService()

    def build_cache_key(self, lat: float, lon: float, radius_m: int) -> SpatialCacheKey:
        return (round(lat, 3), round(lon, 3), radius_m)

    async def get_nearest_venues(
        self, lat: float, lon: float, limit: int, radius_m: int
    ) -> NearestResponse:
        cache_key = self.build_cache_key(lat, lon, radius_m)
        cached_venues = self._cache.get(cache_key)

        if cached_venues is not None:
            venues = cached_venues
        else:
            raw_venues = await self._provider.fetch_venues(lat, lon, radius_m)
            if not raw_venues:
                raise HTTPException(
                    status_code=504,
                    detail=(
                        "OpenStreetMap Service Provider Timeout: No live venue data "
                        "received from OpenStreetMap servers. Please try again."
                    ),
                )
            venues = self._process_raw_venues(raw_venues, lat, lon)
            self._cache.set(cache_key, venues)

        primary_venue = venues[0] if len(venues) > 0 else None
        alternatives = venues[1 : 1 + limit] if len(venues) > 1 else []

        return NearestResponse(
            status="success",
            query_location=Coordinates(latitude=lat, longitude=lon),
            primary_venue=primary_venue,
            alternatives=alternatives,
        )

    def _process_raw_venues(
        self, raw_venues: list[RawVenueData], user_lat: float, user_lon: float
    ) -> list[Venue]:
        processed: list[Venue] = []
        seen_ids: set[str] = set()

        for raw in raw_venues:
            if not raw.name or raw.name.strip() == "":
                continue

            elem_id = f"osm-{raw.osm_type}-{raw.osm_id}"
            if elem_id in seen_ids:
                continue
            seen_ids.add(elem_id)

            tags = raw.raw_tags
            if (
                tags.get("disused") == "yes"
                or tags.get("abandoned") == "yes"
                or raw.venue_type in ["juice", "milk", "coffee", "shisha"]
            ):
                continue

            dist = self._geo_service.haversine_distance(
                user_lat, user_lon, raw.latitude, raw.longitude
            )
            walk_min = self._geo_service.calculate_walking_time_minutes(dist)

            address = (
                Address(street=raw.street, city=raw.city, postcode=raw.postcode)
                if (raw.street or raw.city or raw.postcode)
                else None
            )

            opening_status = (
                OpeningStatus(is_open_now=None, raw=raw.opening_hours)
                if raw.opening_hours
                else None
            )

            maps_url = self._geo_service.build_google_maps_url(raw.latitude, raw.longitude)

            processed.append(
                Venue(
                    id=elem_id,
                    name=raw.name,
                    type=raw.venue_type,
                    distance_meters=dist,
                    walking_time_minutes=walk_min,
                    address=address,
                    opening_status=opening_status,
                    coordinates=Coordinates(latitude=raw.latitude, longitude=raw.longitude),
                    maps_url=maps_url,
                )
            )

        processed.sort(key=lambda v: v.distance_meters)
        return processed
