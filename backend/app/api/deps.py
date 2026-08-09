from collections.abc import AsyncGenerator

import httpx
from fastapi import Request

from app.cache.base import BaseCacheRepository
from app.cache.memory import SpatialLRUCacheRepository
from app.providers.base import BaseGeospatialProvider
from app.providers.chain import ProviderChain
from app.providers.nominatim import NominatimProvider
from app.providers.overpass import OverpassProvider
from app.services.venue_service import VenueService

_spatial_cache_repository: BaseCacheRepository = SpatialLRUCacheRepository()


def get_cache_repository() -> BaseCacheRepository:
    return _spatial_cache_repository


async def get_http_client(request: Request) -> AsyncGenerator[httpx.AsyncClient, None]:
    client: httpx.AsyncClient = request.app.state.http_client
    yield client


def get_provider_chain(
    client: httpx.AsyncClient,
) -> BaseGeospatialProvider:
    nominatim = NominatimProvider(client=client)
    overpass = OverpassProvider(client=client)
    return ProviderChain(providers=[nominatim, overpass])


def get_venue_service(
    request: Request,
) -> VenueService:
    client: httpx.AsyncClient = request.app.state.http_client
    provider = get_provider_chain(client)
    cache = get_cache_repository()
    return VenueService(provider=provider, cache=cache)
