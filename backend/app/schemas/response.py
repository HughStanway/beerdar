from pydantic import BaseModel

from app.schemas.coordinates import Coordinates
from app.schemas.venue import Venue


class NearestResponse(BaseModel):
    status: str = "success"
    query_location: Coordinates
    primary_venue: Venue | None = None
    alternatives: list[Venue] = []


class HealthResponse(BaseModel):
    status: str
    timestamp: str
    service: str
