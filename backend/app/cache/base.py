from abc import ABC, abstractmethod

from app.schemas.venue import Venue

SpatialCacheKey = tuple[float, float, int]


class BaseCacheRepository(ABC):
    @abstractmethod
    def get(self, key: SpatialCacheKey) -> list[Venue] | None:
        pass

    @abstractmethod
    def set(self, key: SpatialCacheKey, value: list[Venue]) -> None:
        pass

    @abstractmethod
    def clear(self) -> None:
        pass
