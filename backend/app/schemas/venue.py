from pydantic import BaseModel

from app.schemas.address import Address
from app.schemas.coordinates import Coordinates
from app.schemas.opening_status import OpeningStatus


class Venue(BaseModel):
    id: str
    name: str
    type: str
    distance_meters: int
    walking_time_minutes: int
    address: Address | None = None
    opening_status: OpeningStatus | None = None
    coordinates: Coordinates
    maps_url: str
