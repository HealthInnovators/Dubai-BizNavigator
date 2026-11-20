"""Core application settings and environment configuration.

Strictly enforces Langfuse observability while disabling LangSmith/competing OTLP exporters.
"""

import os
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration with strict LangSmith disabling."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    PROJECT_NAME: str = "Dubai BizNavigator"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    BACKEND_CORS_ORIGINS: list[str] = Field(
        default=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"]
    )

    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/dubai_biznavigator"

    # Langfuse Observability SDK v3+
    LANGFUSE_PUBLIC_KEY: str = "pk-lf-placeholder"
    LANGFUSE_SECRET_KEY: str = "sk-lf-placeholder"
    LANGFUSE_BASE_URL: str = "https://cloud.langfuse.com"

    # LangSmith / OTLP strictly disabled to prevent TracerProvider conflicts
    LANGSMITH_TRACING: Literal["false"] = "false"
    LANGSMITH_OTEL_ENABLED: Literal["false"] = "false"

    # External APIs
    ANTHROPIC_API_KEY: str = ""
    TAVILY_API_KEY: str = ""

    # Corporate Banking Partner API
    BANKING_API_BASE_URL: str = "https://api.banking-sandbox.uae.ae/v1"
    BANKING_API_KEY: str = "sandbox-key"
    BANKING_WEBHOOK_SECRET: str = "sandbox-secret-uae-biznav"
    BANKING_SANDBOX_MODE: bool = True

    def model_post_init(self, __context: object) -> None:
        """Enforce environment variables to prevent LangSmith auto-initialization."""
        super().model_post_init(__context)
        # Explicitly enforce in os.environ so any third-party SDK reads 'false'
        os.environ["LANGSMITH_TRACING"] = "false"
        os.environ["LANGSMITH_OTEL_ENABLED"] = "false"


settings = Settings()
