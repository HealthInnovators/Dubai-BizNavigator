"""Unit tests for Langfuse observability adapter.

Verifies PII redaction, LangSmith OTLP disabling, attribute propagation,
auth checks, and span scope filtering with mocked Langfuse client.
"""

import os
from unittest.mock import MagicMock, patch

import pytest

from app.core.config import Settings, settings
from app.infrastructure.observability.langfuse_adapter import (
    LangfuseObservabilityAdapter,
)


class TestLangSmithOTLPDisabled:
    """Verify LangSmith OTLP tracing is strictly disabled to prevent conflicts."""

    def test_env_flags_disabled_in_settings(self) -> None:
        assert settings.LANGSMITH_TRACING == "false"
        assert settings.LANGSMITH_OTEL_ENABLED == "false"

    def test_os_environ_enforces_disabled_flags(self) -> None:
        # Re-instantiating settings ensures os.environ receives "false"
        _ = Settings()
        assert os.environ.get("LANGSMITH_TRACING") == "false"
        assert os.environ.get("LANGSMITH_OTEL_ENABLED") == "false"


class TestPIIRedaction:
    """Verify redacting passport numbers, Emirates IDs, IBANs, and API keys."""

    @pytest.fixture
    def adapter(self) -> LangfuseObservabilityAdapter:
        mock_client = MagicMock()
        return LangfuseObservabilityAdapter(
            public_key="pk-test",
            secret_key="sk-test",
            base_url="https://cloud.langfuse.com",
            client=mock_client,
        )

    def test_emirates_id_redaction(self, adapter: LangfuseObservabilityAdapter) -> None:
        formatted = "Founders Emirates ID: 784-1985-1234567-1."
        unformatted = "Emirates ID is 784198512345671 for KYC."
        assert adapter.mask_pii(formatted) == "Founders Emirates ID: [REDACTED_EMIRATES_ID]."
        assert adapter.mask_pii(unformatted) == "Emirates ID is [REDACTED_EMIRATES_ID] for KYC."

    def test_passport_redaction(self, adapter: LangfuseObservabilityAdapter) -> None:
        sample_passport = "Shareholder passport is N12345678 issued in 2022."
        labeled_passport = "passport_number: A98765432 verified."
        assert (
            adapter.mask_pii(sample_passport)
            == "Shareholder passport is [REDACTED_PASSPORT] issued in 2022."
        )
        assert (
            adapter.mask_pii(labeled_passport)
            == "passport_number: [REDACTED_PASSPORT] verified."
        )

    def test_iban_redaction(self, adapter: LangfuseObservabilityAdapter) -> None:
        uae_iban = "Corporate payout to AE070331234567890123456 at Wio Bank."
        assert (
            adapter.mask_pii(uae_iban)
            == "Corporate payout to [REDACTED_IBAN] at Wio Bank."
        )

    def test_api_key_redaction(self, adapter: LangfuseObservabilityAdapter) -> None:
        sk_key = "Using secret key sk-ant-api03-abcdef12345678901234567890."
        pk_key = "Public key pk-lf-1234567890abcdef1234567890."
        bearer = "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ91234567890."
        assert (
            adapter.mask_pii(sk_key)
            == "Using secret key [REDACTED_API_KEY]."
        )
        assert (
            adapter.mask_pii(pk_key)
            == "Public key [REDACTED_API_KEY]."
        )
        assert (
            adapter.mask_pii(bearer)
            == "Authorization: [REDACTED_API_KEY]"
        )

    def test_recursive_nested_structure_redaction(
        self, adapter: LangfuseObservabilityAdapter
    ) -> None:
        payload = {
            "applicant": {
                "name": "Rashid Al Falasi",
                "emirates_id": "784-1990-7654321-2",
                "passports": ["N87654321"],
                "bank": {
                    "iban": "AE250339876543210987654",
                    "api_token": "sk-secret-token-abcdef12345678901234",
                },
            },
            "status": "pending_kyc",
        }
        masked = adapter.mask_pii(payload)
        assert masked["applicant"]["name"] == "Rashid Al Falasi"
        assert masked["applicant"]["emirates_id"] == "[REDACTED_EMIRATES_ID]"
        assert masked["applicant"]["passports"] == ["[REDACTED_PASSPORT]"]
        assert masked["applicant"]["bank"]["iban"] == "[REDACTED_IBAN]"
        assert masked["applicant"]["bank"]["api_token"] == "[REDACTED_API_KEY]"
        assert masked["status"] == "pending_kyc"


class TestAttributePropagationAndIsolation:
    """Verify multi-tenant attribute propagation with PII masking."""

    @patch("app.infrastructure.observability.langfuse_adapter.propagate_attributes")
    def test_propagate_tenant_context(self, mock_propagate: MagicMock) -> None:
        mock_propagate.return_value.__enter__.return_value = None
        adapter = LangfuseObservabilityAdapter(
            public_key="pk-test",
            secret_key="sk-test",
            client=MagicMock(),
        )

        raw_metadata = {
            "tenant": "dubai_corp",
            "founder_emirates_id": "784-1992-1122334-5",
            "bank_iban": "AE070331234567890123456",
        }

        with adapter.propagate_tenant_context(
            user_id="user_uae_001",
            session_id="session_formation_88",
            tags=["freezone", "ifza"],
            metadata=raw_metadata,
            version="1.0.0",
            trace_name="setup_workflow",
        ) as ctx:
            assert ctx["user_id"] == "user_uae_001"
            assert ctx["session_id"] == "session_formation_88"
            assert ctx["metadata"]["founder_emirates_id"] == "[REDACTED_EMIRATES_ID]"
            assert ctx["metadata"]["bank_iban"] == "[REDACTED_IBAN]"

        mock_propagate.assert_called_once()
        _, kwargs = mock_propagate.call_args
        assert kwargs["user_id"] == "user_uae_001"
        assert kwargs["session_id"] == "session_formation_88"
        assert kwargs["tags"] == ["freezone", "ifza"]
        assert kwargs["metadata"]["founder_emirates_id"] == "[REDACTED_EMIRATES_ID]"

    def test_observe_tenant_decorator_sync(self) -> None:
        adapter = LangfuseObservabilityAdapter(
            public_key="pk-test",
            secret_key="sk-test",
            client=MagicMock(),
        )

        @adapter.observe_tenant(name="sync_step", user_id="tenant_1")
        def sample_sync_task(x: int) -> int:
            return x * 2

        assert sample_sync_task(5) == 10

    @pytest.mark.asyncio
    async def test_observe_tenant_decorator_async(self) -> None:
        adapter = LangfuseObservabilityAdapter(
            public_key="pk-test",
            secret_key="sk-test",
            client=MagicMock(),
        )

        @adapter.observe_tenant(name="async_step", user_id="tenant_2")
        async def sample_async_task(x: int) -> int:
            return x + 5

        result = await sample_async_task(10)
        assert result == 15


class TestClientConnectivityAndLifecycle:
    """Verify auth_check, flush, callback handler, and span filtering."""

    def test_auth_check_success(self) -> None:
        mock_client = MagicMock()
        mock_client.auth_check.return_value = True
        adapter = LangfuseObservabilityAdapter(client=mock_client)
        assert adapter.auth_check() is True
        mock_client.auth_check.assert_called_once()

    def test_auth_check_failure(self) -> None:
        mock_client = MagicMock()
        mock_client.auth_check.side_effect = RuntimeError("Connection refused")
        adapter = LangfuseObservabilityAdapter(client=mock_client)
        assert adapter.auth_check() is False

    def test_flush_sync_and_async(self) -> None:
        mock_client = MagicMock()
        adapter = LangfuseObservabilityAdapter(client=mock_client)
        adapter.flush_sync()
        mock_client.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_async_flush_implements_port(self) -> None:
        mock_client = MagicMock()
        adapter = LangfuseObservabilityAdapter(client=mock_client)
        await adapter.flush()
        mock_client.flush.assert_called_once()

    def test_get_langchain_callback_handler(self) -> None:
        adapter = LangfuseObservabilityAdapter(
            public_key="pk-lf-custom",
            secret_key="sk-lf-custom",
            base_url="https://custom.langfuse.com",
            client=MagicMock(),
        )
        handler = adapter.get_langchain_callback_handler()
        assert handler is not None

    def test_instrumentation_scope_filtering(self) -> None:
        adapter = LangfuseObservabilityAdapter(client=MagicMock())
        # Noisy third-party spans should be suppressed
        assert adapter.should_filter_span("opentelemetry.instrumentation.urllib3") is True
        assert adapter.should_filter_span("opentelemetry.instrumentation.requests") is True
        assert adapter.should_filter_span("opentelemetry.instrumentation.httpx") is True
        assert adapter.should_filter_span("opentelemetry.instrumentation.psycopg") is True
        assert adapter.should_filter_span("opentelemetry.instrumentation.sqlalchemy") is True

        # LLM / Agent scopes should NOT be suppressed
        assert adapter.should_filter_span("opentelemetry.instrumentation.langchain") is False
        assert adapter.should_filter_span("opentelemetry.instrumentation.openai") is False
        assert adapter.should_filter_span("langfuse-sdk") is False
        assert adapter.should_filter_span(None) is False
