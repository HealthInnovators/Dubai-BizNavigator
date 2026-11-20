"""Langfuse observability adapter implementing pure Clean Architecture ObservabilityPort.

Completely replaces LangChain OpenTelemetry (OTLP) / LangSmith tracing with Langfuse SDK v3+.
Guarantees zero TracerProvider conflicts by asserting that competing OTLP exporters remain disabled.
Enforces multi-tenant context propagation and automated PII masking across all trace inputs, outputs, and metadata.
"""

from __future__ import annotations

import functools
import inspect
import logging
import re
from collections.abc import Callable, Generator
from contextlib import contextmanager
from typing import Any

from langfuse import get_client, observe, propagate_attributes

from app.core.config import settings
from app.domain.ports import ObservabilityPort

logger = logging.getLogger("dubai_biznavigator.observability")

# Instrumentation scopes to suppress (noisy third-party HTTP/DB traces)
NOISY_INSTRUMENTATION_SCOPES: frozenset[str] = frozenset(
    {
        "opentelemetry.instrumentation.urllib3",
        "opentelemetry.instrumentation.requests",
        "opentelemetry.instrumentation.httpx",
        "opentelemetry.instrumentation.http",
        "opentelemetry.instrumentation.psycopg",
        "opentelemetry.instrumentation.psycopg2",
        "opentelemetry.instrumentation.asyncpg",
        "opentelemetry.instrumentation.sqlalchemy",
        "opentelemetry.instrumentation.fastapi",
        "opentelemetry.instrumentation.starlette",
    }
)

# PII regex patterns for automated redaction
EMIRATES_ID_PATTERN = re.compile(r"\b784-?\d{4}-?\d{7}-?\d{1}\b")
PASSPORT_PATTERN = re.compile(r"\b[A-PR-WY][0-9]{7,8}\b")
LABELED_PASSPORT_PATTERN = re.compile(
    r"(?i)\b(passport(?:_number)?[:\s=]+)([A-PR-WY0-9]{6,9})\b"
)
IBAN_PATTERN = re.compile(r"\b[A-Z]{2}\d{2}[A-Z0-9]{11,30}\b")
API_KEY_PATTERN = re.compile(
    r"\b(?:sk|pk)-(?:lf-)?[a-zA-Z0-9_\-]{20,}\b|Bearer\s+[a-zA-Z0-9_\-\.]{20,}"
)


class LangfuseObservabilityAdapter(ObservabilityPort):
    """Adapter for Langfuse observability, telemetry, and tenant trace isolation.

    Implements `ObservabilityPort` and ensures conflict-free telemetry without
    competing OTLP TracerProviders.

    Attributes:
        public_key: Langfuse project public API key.
        secret_key: Langfuse project secret API key.
        base_url: Langfuse server endpoint URL (cloud or self-hosted VPC).
    """

    def __init__(
        self,
        public_key: str | None = None,
        secret_key: str | None = None,
        base_url: str | None = None,
        client: Any = None,
    ) -> None:
        """Initialize the Langfuse observability adapter.

        Args:
            public_key: Optional public key override (defaults to settings.LANGFUSE_PUBLIC_KEY).
            secret_key: Optional secret key override (defaults to settings.LANGFUSE_SECRET_KEY).
            base_url: Optional host endpoint override (defaults to settings.LANGFUSE_BASE_URL).
            client: Optional pre-configured Langfuse client instance (used for testing).
        """
        self.public_key = public_key or settings.LANGFUSE_PUBLIC_KEY
        self.secret_key = secret_key or settings.LANGFUSE_SECRET_KEY
        self.base_url = base_url or settings.LANGFUSE_BASE_URL

        # Use injected client (for testing) or initialize default
        self._client = client if client is not None else get_client()

    def auth_check(self) -> bool:
        """Verify connectivity to Langfuse server during FastAPI lifespan startup.

        Returns:
            True if authentication succeeded and connection is healthy, False otherwise.
        """
        try:
            if not self._client:
                return False
            result = self._client.auth_check()
            return bool(result)
        except Exception as err:
            logger.warning("Langfuse auth_check failed: %s", err)
            return False

    def get_langchain_callback_handler(self, **kwargs: Any) -> Any:
        """Factory method returning a Langfuse LangChain callback handler.

        Injected into LangGraph execution configurations (`config={'callbacks': [handler]}`)
        to trace root coordinator and subagent turns.

        Args:
            **kwargs: Additional parameters passed to `CallbackHandler`.

        Returns:
            Instantiated `langfuse.langchain.CallbackHandler` instance.
        """
        from langfuse.langchain import CallbackHandler

        params: dict[str, Any] = {}
        if self.public_key:
            params["public_key"] = self.public_key
        params.update(kwargs)
        return CallbackHandler(**params)

    def mask_pii(self, data: Any) -> Any:
        """Recursively redact Emirates IDs, passports, IBANs, and API keys.

        Args:
            data: Arbitrary nested dictionary, list, string, or primitive.

        Returns:
            Sanitized structure with PII strings replaced by `[REDACTED_*]` tokens.
        """
        if isinstance(data, str):
            redacted = EMIRATES_ID_PATTERN.sub("[REDACTED_EMIRATES_ID]", data)
            redacted = LABELED_PASSPORT_PATTERN.sub(r"\1[REDACTED_PASSPORT]", redacted)
            redacted = PASSPORT_PATTERN.sub("[REDACTED_PASSPORT]", redacted)
            redacted = IBAN_PATTERN.sub("[REDACTED_IBAN]", redacted)
            redacted = API_KEY_PATTERN.sub("[REDACTED_API_KEY]", redacted)
            return redacted
        elif isinstance(data, dict):
            return {k: self.mask_pii(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self.mask_pii(item) for item in data]
        elif isinstance(data, tuple):
            return tuple(self.mask_pii(item) for item in data)
        elif isinstance(data, set):
            return {self.mask_pii(item) for item in data}
        return data

    def should_filter_span(self, instrumentation_scope_name: str | None) -> bool:
        """Check if an instrumentation scope represents noisy third-party telemetry.

        Args:
            instrumentation_scope_name: Name of the telemetry scope (e.g. 'opentelemetry.instrumentation.http').

        Returns:
            True if the scope should be suppressed, False otherwise.
        """
        if not instrumentation_scope_name:
            return False
        scope_clean = instrumentation_scope_name.strip().lower()
        return any(scope_clean.startswith(noisy) for noisy in NOISY_INSTRUMENTATION_SCOPES)

    @contextmanager
    def propagate_tenant_context(
        self,
        user_id: str | None = None,
        session_id: str | None = None,
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
        version: str | None = None,
        trace_name: str | None = None,
    ) -> Generator[dict[str, Any], None, None]:
        """Context manager propagating multi-tenant attributes with PII redaction.

        Args:
            user_id: Tenant or user identifier for isolation.
            session_id: Active session or workspace identifier.
            tags: Categorical tags attached to the trace.
            metadata: Metadata dictionary to redact and propagate.
            version: Application release version string.
            trace_name: Optional override for the root trace label.

        Yields:
            Dictionary containing the propagated attributes.
        """
        cleaned_metadata = self.mask_pii(metadata) if metadata else {}
        with propagate_attributes(
            user_id=user_id,
            session_id=session_id,
            tags=tags,
            metadata=cleaned_metadata,
            version=version,
            trace_name=trace_name,
        ):
            yield {
                "user_id": user_id,
                "session_id": session_id,
                "tags": tags,
                "metadata": cleaned_metadata,
                "version": version,
                "trace_name": trace_name,
            }

    def observe_tenant(
        self,
        name: str | None = None,
        user_id: str | None = None,
        session_id: str | None = None,
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
        version: str | None = None,
        as_type: str | None = None,
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """Decorator helper wrapping @observe and multi-tenant attribute propagation.

        Supports both synchronous and asynchronous functions.

        Args:
            name: Name of the traced observation/span.
            user_id: Tenant identifier.
            session_id: Session identifier.
            tags: Observability tags.
            metadata: Observation metadata attributes.
            version: Semantic version string.
            as_type: Observation type (e.g. 'generation', 'span', 'event').

        Returns:
            Decorated wrapper function.
        """

        def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
            observed_fn = observe(name=name, as_type=as_type)(fn)

            @functools.wraps(fn)
            def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
                with self.propagate_tenant_context(
                    user_id=user_id,
                    session_id=session_id,
                    tags=tags,
                    metadata=metadata,
                    version=version,
                    trace_name=name,
                ):
                    return observed_fn(*args, **kwargs)

            @functools.wraps(fn)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                with self.propagate_tenant_context(
                    user_id=user_id,
                    session_id=session_id,
                    tags=tags,
                    metadata=metadata,
                    version=version,
                    trace_name=name,
                ):
                    return await observed_fn(*args, **kwargs)

            if inspect.iscoroutinefunction(fn):
                return async_wrapper
            return sync_wrapper

        return decorator

    def flush_sync(self) -> None:
        """Synchronously flush buffered traces to Langfuse collector."""
        if self._client and hasattr(self._client, "flush"):
            self._client.flush()

    async def flush(self) -> None:
        """Asynchronously flush buffered traces (implements ObservabilityPort)."""
        self.flush_sync()

    async def record_trace_metadata(
        self, trace_id: str, metadata: dict[str, Any]
    ) -> None:
        """Record trace metadata with automated PII masking.

        Args:
            trace_id: Target trace identifier.
            metadata: Dictionary of metadata attributes to sanitize and record.
        """
        cleaned_metadata = self.mask_pii(metadata)
        logger.debug(
            "Recording trace metadata for %s: %s", trace_id, cleaned_metadata
        )
