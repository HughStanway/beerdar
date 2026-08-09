from datetime import UTC, datetime

from fastapi import APIRouter

from app.schemas.response import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["Health"])
def health_check() -> HealthResponse:
    """System health check endpoint used by container orchestrators and CI/CD deployment engines."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(UTC).isoformat(),
        service="pubfinder-api",
    )
