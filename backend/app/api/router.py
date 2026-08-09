from fastapi import APIRouter

from app.api.v1.endpoints import health, venues
from app.core.config import settings

api_router = APIRouter()

api_router.include_router(health.router)

v1_router = APIRouter(prefix=settings.API_V1_STR)
v1_router.include_router(venues.router)

api_router.include_router(v1_router)
