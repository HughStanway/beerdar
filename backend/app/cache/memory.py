import logging

from cachetools import TTLCache

from app.cache.base import BaseCacheRepository, SpatialCacheKey
from app.core.config import settings
from app.schemas.venue import Venue

logger = logging.getLogger(__name__)


class SpatialLRUCacheRepository(BaseCacheRepository):
    def __init__(
        self,
        maxsize: int = settings.CACHE_MAX_SIZE,
        ttl: int = settings.CACHE_TTL_SECONDS,
    ):
        self._cache: TTLCache[SpatialCacheKey, list[Venue]] = TTLCache(maxsize=maxsize, ttl=ttl)

    def get(self, key: SpatialCacheKey) -> list[Venue] | None:
        if key in self._cache:
            logger.info(f"Spatial cache HIT for key {key}")
            return self._cache[key]
        logger.info(f"Spatial cache MISS for key {key}")
        return None

    def set(self, key: SpatialCacheKey, value: list[Venue]) -> None:
        self._cache[key] = value
        logger.info(f"Stored {len(value)} venues in spatial cache under key {key}")

    def clear(self) -> None:
        self._cache.clear()
        logger.info("Cleared all spatial cache entries.")
