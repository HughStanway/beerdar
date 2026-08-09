from collections.abc import AsyncGenerator

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.api.deps import get_cache_repository
from app.factory import create_app


@pytest.fixture
def app() -> FastAPI:
    app_instance = create_app()
    cache = get_cache_repository()
    cache.clear()
    return app_instance


@pytest.fixture
async def async_client(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    async with app.router.lifespan_context(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            yield client
