from pydantic import BaseModel, Field


class Coordinates(BaseModel):
    """WGS84 latitude and longitude coordinates."""

    latitude: float = Field(..., ge=-90.0, le=90.0, description="Latitude in decimal degrees")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="Longitude in decimal degrees")
