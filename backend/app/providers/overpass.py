import logging
from typing import Any

import httpx

from app.core.config import settings
from app.providers.base import BaseGeospatialProvider, RawVenueData

logger = logging.getLogger(__name__)


class OverpassProvider(BaseGeospatialProvider):
    """OpenStreetMap Overpass API Provider (Secondary / Fallback provider)."""

    def __init__(
        self,
        client: httpx.AsyncClient,
        url: str = settings.OVERPASS_URL,
        user_agent: str = settings.USER_AGENT,
        timeout: float = settings.HTTP_TIMEOUT_SECONDS,
    ):
        self._client = client
        self._url = url
        self._user_agent = user_agent
        self._timeout = timeout

    @property
    def name(self) -> str:
        return "Overpass"

    async def fetch_venues(self, lat: float, lon: float, radius_m: int) -> list[RawVenueData]:
        effective_radius = min(radius_m, 3000)
        query = f"""
        [out:json][timeout:6];
        (
          node["amenity"="pub"](around:{effective_radius}, {lat}, {lon});
          node["amenity"="bar"](around:{effective_radius}, {lat}, {lon});
          node["craft"="brewery"](around:{effective_radius}, {lat}, {lon});
          node["microbrewery"="yes"](around:{effective_radius}, {lat}, {lon});
        );
        out body;
        """
        headers = {"User-Agent": self._user_agent}

        try:
            resp = await self._client.post(
                self._url,
                data={"data": query},
                headers=headers,
                timeout=self._timeout,
            )
            resp.raise_for_status()
            data = resp.json()
            elements = data.get("elements", [])

            results: list[RawVenueData] = []
            for elem in elements:
                parsed = self._parse_element(elem)
                if parsed:
                    results.append(parsed)
            return results
        except Exception as exc:
            logger.warning(f"Overpass query failed: {exc}")
            return []

    def _parse_element(self, elem: dict[str, Any]) -> RawVenueData | None:
        tags = elem.get("tags", {})
        name = tags.get("name") or tags.get("name:en")
        if not name or name.strip() == "":
            return None

        v_lat = elem.get("lat")
        v_lon = elem.get("lon")
        if v_lat is None or v_lon is None:
            return None

        venue_type = tags.get("amenity") or tags.get("craft") or "pub"
        street = tags.get("addr:street")
        city = tags.get("addr:city") or tags.get("addr:town")
        postcode = tags.get("addr:postcode")
        opening_hours = tags.get("opening_hours")

        return RawVenueData(
            osm_id=int(elem.get("id", 0)),
            osm_type=str(elem.get("type", "node")),
            name=name.strip(),
            venue_type=venue_type,
            latitude=float(v_lat),
            longitude=float(v_lon),
            street=street,
            city=city,
            postcode=postcode,
            opening_hours=opening_hours,
            raw_tags=tags,
        )
