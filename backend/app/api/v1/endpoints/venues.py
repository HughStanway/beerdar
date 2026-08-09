from fastapi import APIRouter, Depends, Query

from app.api.deps import get_venue_service
from app.schemas.response import NearestResponse
from app.services.venue_service import VenueService

router = APIRouter()


@router.get("/nearest", response_model=NearestResponse, tags=["Venues"])
async def get_nearest_venues(
    lat: float = Query(..., description="User latitude", ge=-90.0, le=90.0),
    lon: float = Query(..., description="User longitude", ge=-180.0, le=180.0),
    limit: int = Query(1, description="Number of primary/alternative venues", ge=1, le=20),
    radius_m: int = Query(5000, description="Search radius in meters", ge=100, le=50000),
    venue_service: VenueService = Depends(get_venue_service),
) -> NearestResponse:
    """Find nearest pubs, bars, microbreweries, and taprooms around user coordinates."""
    return await venue_service.get_nearest_venues(lat=lat, lon=lon, limit=limit, radius_m=radius_m)
