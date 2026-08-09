import logging

from app.providers.base import BaseGeospatialProvider, RawVenueData

logger = logging.getLogger(__name__)


class ProviderChain(BaseGeospatialProvider):
    """Composite Provider Strategy executing sequential provider queries with graceful failover."""

    def __init__(self, providers: list[BaseGeospatialProvider]):
        if not providers:
            raise ValueError("ProviderChain requires at least one provider.")
        self._providers = providers

    @property
    def name(self) -> str:
        return f"ProviderChain([{', '.join(p.name for p in self._providers)}])"

    async def fetch_venues(self, lat: float, lon: float, radius_m: int) -> list[RawVenueData]:
        for provider in self._providers:
            logger.info(f"Querying provider '{provider.name}'...")
            try:
                results = await provider.fetch_venues(lat, lon, radius_m)
                if results and len(results) > 0:
                    logger.info(f"Provider '{provider.name}' returned {len(results)} raw venues.")
                    return results
                else:
                    logger.info(
                        f"Provider '{provider.name}' returned 0 results. Trying next provider..."
                    )
            except Exception as exc:
                logger.warning(
                    f"Provider '{provider.name}' failed with error: {exc}. Trying next..."
                )

        logger.error("All providers in ProviderChain failed or returned 0 results.")
        return []
