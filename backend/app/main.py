"""FastAPI entrypoint with lifespan hooks and Clean Architecture routing."""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.infrastructure.config import settings
from app.interfaces.api.v1.endpoints.health import HealthResponse
from app.interfaces.api.v1.router import api_v1_router
from app.interfaces.container import get_container

logger = logging.getLogger("dubai_biznavigator")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Lifespan context manager for startup and shutdown events."""
    logger.info("Initializing Dubai BizNavigator backend...")
    # Initialize DI Container and services
    container = get_container()
    logger.info("DI Container ready with DB: %s", container.settings.DATABASE_URL)

    # Verify Langfuse observability connectivity with auth_check
    if hasattr(container, "observability") and container.observability:
        is_connected = container.observability.auth_check()
        if is_connected:
            logger.info("Langfuse connectivity verified successfully.")
        else:
            logger.info("Langfuse initialized (auth_check status: %s).", is_connected)

    yield

    # Flush observability events on shutdown
    if hasattr(container, "observability") and container.observability:
        await container.observability.flush()

    logger.info("Shutting down Dubai BizNavigator backend...")


def create_app() -> FastAPI:
    """Application factory for FastAPI instance."""
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version="0.1.0",
        description="Clean Architecture backend for Dubai Business Setup Orchestration",
        lifespan=lifespan,
    )

    # CORS configuration
    if settings.BACKEND_CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Direct top-level health endpoint
    @app.get("/health", response_model=HealthResponse, tags=["Health"])
    async def top_level_health() -> HealthResponse:
        return HealthResponse(
            status="ok",
            app="Dubai BizNavigator",
            environment=settings.ENVIRONMENT,
        )

    # Include versioned API routers
    app.include_router(api_v1_router, prefix="/api/v1")

    # Include BizNavigator workflow & session routes (/v1/...)
    from app.interfaces.api.routes import router as workflow_router
    app.include_router(workflow_router)

    return app


app = create_app()
