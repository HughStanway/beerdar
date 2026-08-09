import logging
from typing import Any

import httpx

from app.core.config import settings
from app.providers.base import BaseGeospatialProvider, RawVenueData

logger = logging.getLogger(__name__)


class NominatimProvider(BaseGeospatialProvider):
    """High-speed OpenStreetMap Nominatim Search Engine provider."""

    def __init__(
        self,
        client: httpx.AsyncClient,
        url: str = settings.NOMINATIM_URL,
        user_agent: str = settings.USER_AGENT,
        timeout: float = settings.HTTP_TIMEOUT_SECONDS,
    ):
        self._client = client
        self._url = url
        self._user_agent = user_agent
        self._timeout = timeout

    @property
    def name(self) -> str:
        return "Nominatim"

    async def fetch_venues(self, lat: float, lon: float, radius_m: int) -> list[RawVenueData]:
        delta = 0.035
        viewbox = f"{lon - delta},{lat + delta},{lon + delta},{lat - delta}"
        headers = {"User-Agent": self._user_agent}

        raw_results: list[RawVenueData] = []
        for amenity_type in ["pub", "bar", "brewery"]:
            url = (
                f"{self._url}?format=jsonv2&amenity={amenity_type}"
                f"&lat={lat}&lon={lon}&bounded=1&viewbox={viewbox}&limit=25&addressdetails=1"
            )
            try:
                resp = await self._client.get(url, headers=headers, timeout=self._timeout)
                if resp.status_code == 200:
                    items = resp.json()
                    for item in items:
                        parsed = self._parse_item(item)
                        if parsed:
                            raw_results.append(parsed)
            except Exception as exc:
                logger.warning(f"Nominatim query for {amenity_type} failed: {exc}")

        return raw_results

    def _parse_item(self, item: dict[str, Any]) -> RawVenueData | None:
        name = item.get("name") or item.get("display_name", "").split(",")[0]
        if not name or name.strip() == "":
            return None

        try:
            v_lat = float(item.get("lat", 0))
            v_lon = float(item.get("lon", 0))
        except (ValueError, TypeError):
            return None

        addr = item.get("address", {})
        street = addr.get("road") or addr.get("pedestrian") or addr.get("street")
        city = addr.get("city") or addr.get("town") or addr.get("village") or addr.get("suburb")
        postcode = addr.get("postcode")
        venue_type = item.get("type") or "pub"

        return RawVenueData(
            osm_id=int(item.get("osm_id", 0)),
            osm_type=str(item.get("osm_type", "node")),
            name=name.strip(),
            venue_type=venue_type,
            latitude=v_lat,
            longitude=v_lon,
            street=street,
            city=city,
            postcode=postcode,
            raw_tags=addr,
        )
