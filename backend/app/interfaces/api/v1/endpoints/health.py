"""Health check endpoint."""

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["Health"])


class HealthResponse(BaseModel):
    status: str
    app: str
    environment: str


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Return health check status."""
    return HealthResponse(
        status="ok",
        app="Dubai BizNavigator",
        environment="ready",
    )
