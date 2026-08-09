from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel


class RawVenueData(BaseModel):
    """Normalized raw venue data produced by a provider."""

    osm_id: int
    osm_type: str
    name: str
    venue_type: str
    latitude: float
    longitude: float
    street: str | None = None
    city: str | None = None
    postcode: str | None = None
    opening_hours: str | None = None
    raw_tags: dict[str, Any] = {}


class BaseGeospatialProvider(ABC):
    """Abstract Strategy interface for external geospatial data providers."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider identifier name."""
        pass

    @abstractmethod
    async def fetch_venues(self, lat: float, lon: float, radius_m: int) -> list[RawVenueData]:
        """Fetch raw venue data around specified coordinates."""
        pass
