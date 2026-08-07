import pytest
from fastapi.testclient import TestClient
from main import app, haversine_distance, spatial_cache

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "pubfinder-api"
    assert "timestamp" in data


def test_haversine_distance():
    # Distance between London Eye (51.5033, -0.1195) and Big Ben (51.5007, -0.1246) is approx 470m
    dist = haversine_distance(51.5033, -0.1195, 51.5007, -0.1246)
    assert 440 <= dist <= 500


def test_get_nearest_venues_mocked(monkeypatch):
    spatial_cache.clear()

    # Mock response from Overpass API
    mock_overpass_response = {
        "elements": [
            {
                "type": "node",
                "id": 101,
                "lat": 51.8119,
                "lon": -0.0291,
                "tags": {
                    "name": "The Saracens Head",
                    "amenity": "pub",
                    "addr:street": "High Street",
                    "addr:city": "Ware",
                    "addr:postcode": "SG12 9BP",
                    "opening_hours": "Mo-Su 12:00-23:00"
                }
            },
            {
                "type": "node",
                "id": 102,
                "lat": 51.8105,
                "lon": -0.0310,
                "tags": {
                    "name": "Waterside Inn",
                    "amenity": "pub"
                }
            }
        ]
    }

    class MockAsyncClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass

        async def post(self, url, data=None, headers=None, **kwargs):
            class MockResponse:
                status_code = 200

                def raise_for_status(self):
                    pass

                def json(self):
                    return mock_overpass_response

            return MockResponse()

    monkeypatch.setattr("httpx.AsyncClient", MockAsyncClient)

    response = client.get("/api/v1/nearest?lat=51.8115&lon=-0.0298&limit=2")
    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "success"
    assert data["query_location"]["latitude"] == 51.8115
    assert data["query_location"]["longitude"] == -0.0298
    assert data["primary_venue"]["name"] == "The Saracens Head"
    assert data["primary_venue"]["type"] == "pub"
    assert data["primary_venue"]["address"]["city"] == "Ware"
    assert len(data["alternatives"]) == 1
    assert data["alternatives"][0]["name"] == "Waterside Inn"

    # Verify cache hit on second call
    response_cached = client.get("/api/v1/nearest?lat=51.8115&lon=-0.0298&limit=2")
    assert response_cached.status_code == 200
    assert response_cached.json()["primary_venue"]["id"] == "osm-node-101"
