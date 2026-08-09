from typing import Any

import pytest
from httpx import AsyncClient, Response

from app.api.deps import get_cache_repository
from app.providers.base import BaseGeospatialProvider, RawVenueData


class MockGeospatialProvider(BaseGeospatialProvider):
    @property
    def name(self) -> str:
        return "MockProvider"

    async def fetch_venues(self, lat: float, lon: float, radius_m: int) -> list[RawVenueData]:
        return [
            RawVenueData(
                osm_id=101,
                osm_type="node",
                name="The Saracens Head",
                venue_type="pub",
                latitude=51.8119,
                longitude=-0.0291,
                street="High Street",
                city="Ware",
                postcode="SG12 9BP",
                opening_hours="Mo-Su 12:00-23:00",
            ),
            RawVenueData(
                osm_id=102,
                osm_type="node",
                name="Waterside Inn",
                venue_type="pub",
                latitude=51.8105,
                longitude=-0.0310,
                street="Water Lane",
                city="Ware",
                postcode="SG12 9HL",
            ),
        ]


@pytest.mark.asyncio
async def test_get_nearest_venues_mocked(
    async_client: AsyncClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    cache = get_cache_repository()
    cache.clear()

    def mock_get_provider_chain(*args: Any, **kwargs: Any) -> BaseGeospatialProvider:
        return MockGeospatialProvider()

    monkeypatch.setattr("app.api.deps.get_provider_chain", mock_get_provider_chain)

    response = await async_client.get("/api/v1/nearest?lat=51.8115&lon=-0.0298&limit=2")
    assert response.status_code == 200
    data: dict[str, Any] = response.json()

    assert data["status"] == "success"
    assert data["query_location"]["latitude"] == 51.8115
    assert data["query_location"]["longitude"] == -0.0298
    assert data["primary_venue"]["name"] == "The Saracens Head"
    assert data["primary_venue"]["type"] == "pub"
    assert data["primary_venue"]["address"]["city"] == "Ware"
    assert len(data["alternatives"]) == 1
    assert data["alternatives"][0]["name"] == "Waterside Inn"

    response_cached: Response = await async_client.get(
        "/api/v1/nearest?lat=51.8115&lon=-0.0298&limit=2"
    )
    assert response_cached.status_code == 200
    assert response_cached.json()["primary_venue"]["id"] == "osm-node-101"
