"""Integration tests for BizNavigator API workflow, SSE streaming, HITL gates, and banking webhooks."""

import hashlib
import hmac
import json
from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock

import httpx
import pytest
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient

from app.domain.entities import AgentProgressEvent, BankingReadinessPackage, StartupProfile
from app.infrastructure.banking.corporate_banking_adapter import CorporateBankingAdapter
from app.infrastructure.config import settings
from app.interfaces.container import Container, get_container
from app.main import app


class MockStreamingOrchestrator:
    """Mock orchestrator simulating subagent events and HITL interrupts for deterministic tests."""

    def __init__(self) -> None:
        self.should_interrupt = True

    async def stream_subagents(
        self,
        profile: StartupProfile,
        workspace_id: str | None = None,
        session_id: str | None = None,
        tenant_id: str | None = None,
    ) -> AsyncGenerator[AgentProgressEvent, None]:
        yield AgentProgressEvent(
            agent_name="coordinator",
            status="started",
            message=f"Initialized workflow for {profile.company_name}.",
        )
        yield AgentProgressEvent(
            agent_name="licensing-strategist",
            status="running",
            message="Evaluating Dubai Mainland (DET) vs Free Zones.",
            tool_call={"name": "query_uae_regulations", "args": {"authority": "DET"}},
        )
        yield AgentProgressEvent(
            agent_name="licensing-strategist",
            status="running",
            artifact_updated="/workspace/licensing_matrix.md",
            message="Scored licensing matrix generated.",
        )
        if self.should_interrupt:
            yield AgentProgressEvent(
                agent_name="form-automation-agent",
                status="interrupted",
                hitl_interrupt=True,
                message="User approval required for DET registration payload dispatch.",
                payload={
                    "target_authority": "DET",
                    "licence_category": "Commercial",
                    "trade_name": profile.company_name,
                },
            )

    async def resume_execution(
        self,
        resume_action: str,
        session_id: str,
        tenant_id: str | None = None,
    ) -> AsyncGenerator[AgentProgressEvent, None]:
        yield AgentProgressEvent(
            agent_name="coordinator",
            status="running",
            message=f"Resumed workflow with action: {resume_action}",
        )
        yield AgentProgressEvent(
            agent_name="banking-readiness-agent",
            status="running",
            artifact_updated="/workspace/business_plan.md",
            message="Drafted corporate banking business plan.",
        )
        yield AgentProgressEvent(
            agent_name="compliance-auditor",
            status="completed",
            message="Audited compliance readiness with 0 PII leaks.",
        )


@pytest.fixture
def mock_container() -> Container:
    """Provide a container with mock orchestrator for integration testing."""
    c = Container()
    mock_orch = MockStreamingOrchestrator()
    c.orchestrator = mock_orch
    c.process_message_use_case.orchestrator = mock_orch
    c.approve_hitl_use_case.orchestrator = mock_orch
    return c


@pytest.fixture
def client(mock_container: Container) -> TestClient:
    """TestClient wired with mock container."""
    app.dependency_overrides[get_container] = lambda: mock_container
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.mark.asyncio
class TestAPIWorkflowIntegration:
    """Integration test suite covering REST sessions, SSE streaming, HITL, and artifacts."""

    async def test_session_lifecycle_and_artifacts(self, mock_container: Container):
        app.dependency_overrides[get_container] = lambda: mock_container

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            # 1. Create setup session
            payload = {
                "company_name": "Apex AI Global FZ-LLC",
                "industry_sector": "Technology",
                "business_activity": "AI Software Solutions",
                "revenue_model": "B2B_SaaS",
                "uae_local_trade": False,
                "visa_quota_needed": 4,
                "office_preference": "FlexiDesk",
                "founders_summary": "2 Co-founders with UK and UAE residency.",
            }
            res_create = await ac.post("/v1/sessions", json=payload)
            assert res_create.status_code == 201
            session_data = res_create.json()

            session_id = session_data["session_id"]
            workspace_id = session_data["workspace_id"]
            assert session_id.startswith("sess_")
            assert session_data["status"] == "created"
            assert (
                session_data["profile"]["company_name"] == "Apex AI Global FZ-LLC"
            )

            # 2. Retrieve workspace artifacts
            res_art = await ac.get(f"/v1/workspaces/{workspace_id}/artifacts")
            assert res_art.status_code == 200
            artifacts_data = res_art.json()

            assert artifacts_data["workspace_id"] == workspace_id
            assert "artifacts" in artifacts_data
            assert "workspace_files" in artifacts_data
            assert (
                artifacts_data["artifacts"]["startup_profile"]["company_name"]
                == "Apex AI Global FZ-LLC"
            )
            assert "/workspace/startup_profile.json" in artifacts_data["workspace_files"]
            assert "/workspace/licensing_matrix.md" in artifacts_data["workspace_files"]

        app.dependency_overrides.clear()

    async def test_sse_streaming_and_hitl_approval(self, mock_container: Container):
        app.dependency_overrides[get_container] = lambda: mock_container

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            # 1. Initialize session
            sess_res = await ac.post(
                "/v1/sessions",
                json={"company_name": "Falcon Autonomous Systems LLC"},
            )
            assert sess_res.status_code == 201
            session_id = sess_res.json()["session_id"]
            workspace_id = sess_res.json()["workspace_id"]

            # 2. Stream user message and verify A2UI + Agent events
            stream_chunks: list[str] = []
            async with ac.stream(
                "POST",
                f"/v1/sessions/{session_id}/messages",
                json={
                    "message": "Evaluate Dubai licensing options and prepare filing",
                    "workspace_id": workspace_id,
                },
            ) as response:
                assert response.status_code == 200
                assert "text/event-stream" in response.headers.get("content-type", "")

                async for line in response.aiter_lines():
                    if line:
                        stream_chunks.append(line)

            full_stream = "\n".join(stream_chunks)

            # Check that agent progress events are streamed
            assert "event: agent_progress" in full_stream
            assert "Evaluating Dubai Mainland" in full_stream

            # Check that HITL interrupt generates A2UI declarative surface
            assert "event: hitl_interrupt" in full_stream
            assert "event: a2ui_surface" in full_stream
            assert "createSurface" in full_stream
            assert "updateComponents" in full_stream

            # 3. Approve HITL gate and resume execution
            resume_chunks: list[str] = []
            async with ac.stream(
                "POST",
                f"/v1/sessions/{session_id}/approve",
                json={
                    "action": "hitl_approve",
                    "workspace_id": workspace_id,
                    "payload_updates": {"target_authority": "DET Dubai"},
                },
            ) as resume_resp:
                assert resume_resp.status_code == 200
                assert "text/event-stream" in resume_resp.headers.get(
                    "content-type", ""
                )

                async for line in resume_resp.aiter_lines():
                    if line:
                        resume_chunks.append(line)

            resume_stream_text = "\n".join(resume_chunks)
            assert "event: agent_progress" in resume_stream_text
            assert "Resumed workflow with action: hitl_approve" in resume_stream_text

            # Verify repository state: registration payload marked approved
            saved_reg = await mock_container.repository.get_registration_payload(
                workspace_id
            )
            assert saved_reg is not None
            assert saved_reg.hitl_approved is True
            assert saved_reg.approved_at is not None

        app.dependency_overrides.clear()


class TestBankingWebhookSignatureVerification:
    """Integration test suite for banking partner webhook authentication and handling."""

    def test_missing_signature_header(self, client: TestClient):
        response = client.post(
            "/v1/webhooks/banking",
            json={"event": "kyc.verified", "application_id": "app_999"},
        )
        assert response.status_code == 401
        assert "Missing signature header" in response.json()["detail"]

    def test_invalid_signature_header(self, client: TestClient):
        response = client.post(
            "/v1/webhooks/banking",
            json={"event": "kyc.verified", "application_id": "app_999"},
            headers={"X-Banking-Signature": "sha256=invalid_hash_string_here"},
        )
        assert response.status_code == 401
        assert "Invalid HMAC-SHA256 signature" in response.json()["detail"]

    def test_valid_signature_with_x_banking_signature(self, client: TestClient):
        payload = {
            "event": "kyc.application_approved",
            "event_id": "evt_bank_001",
            "application_id": "app_dubai_101",
            "status": "active",
        }
        body_bytes = json.dumps(payload).encode("utf-8")
        secret = settings.BANKING_WEBHOOK_SECRET
        sig_hex = hmac.new(
            secret.encode("utf-8"), body_bytes, hashlib.sha256
        ).hexdigest()

        response = client.post(
            "/v1/webhooks/banking",
            content=body_bytes,
            headers={
                "X-Banking-Signature": f"sha256={sig_hex}",
                "Content-Type": "application/json",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "received"
        assert data["event"] == "kyc.application_approved"
        assert data["application_id"] == "app_dubai_101"

    def test_valid_signature_with_x_hub_signature_and_plain_hex(
        self, client: TestClient
    ):
        payload = {
            "event": "kyb.verification_completed",
            "event_id": "evt_bank_002",
            "submission_id": "sub_909",
        }
        body_bytes = json.dumps(payload).encode("utf-8")
        secret = settings.BANKING_WEBHOOK_SECRET
        sig_hex = hmac.new(
            secret.encode("utf-8"), body_bytes, hashlib.sha256
        ).hexdigest()

        response = client.post(
            "/v1/webhooks/banking",
            content=body_bytes,
            headers={
                "X-Hub-Signature-256": sig_hex,  # plain hex without prefix
                "Content-Type": "application/json",
            },
        )
        assert response.status_code == 200
        assert response.json()["status"] == "received"


@pytest.mark.asyncio
class TestCorporateBankingAdapter:
    """Unit and integration tests for CorporateBankingAdapter."""

    async def test_sandbox_mode_kyc_and_submission(self):
        adapter = CorporateBankingAdapter(sandbox_mode=True)

        # Test KYC checklist
        checklist = await adapter.fetch_kyc_checklist(
            bank_partner_id="Wio_Business", licence_category="Commercial"
        )
        assert len(checklist) >= 8
        assert any("Trade License" in item for item in checklist)
        assert any("Wio Digital Onboarding" in item for item in checklist)

        # Test dossier submission
        package = BankingReadinessPackage(
            bank_partner_id="Wio_Business_API",
            kyc_kyb_checklist=checklist,
            business_plan_markdown="# Plan Details for Corporate Bank Account",
            financial_projection_12m={"revenue": 1000000},
            readiness_score=94.5,
        )
        result = await adapter.submit_readiness_package(
            package=package, workspace_id="ws_sandbox_001"
        )
        assert result["status"] == "submitted"
        assert result["sandbox"] is True
        assert result["readiness_score"] == 94.5
        assert "idemp_ws_sandbox_001" in result["idempotency_key"]

    async def test_signature_verification_helpers(self):
        adapter = CorporateBankingAdapter()
        secret = "test-secret-123"
        data = b'{"status": "ready"}'
        valid_hash = hmac.new(secret.encode(), data, hashlib.sha256).hexdigest()

        assert await adapter.verify_webhook_signature(
            data, f"sha256={valid_hash}", secret
        )
        assert await adapter.verify_webhook_signature(
            data, f"v1={valid_hash}", secret
        )
        assert await adapter.verify_webhook_signature(data, valid_hash, secret)
        assert not await adapter.verify_webhook_signature(data, "bad_hash", secret)
        assert not await adapter.verify_webhook_signature(
            data, valid_hash, "wrong-secret"
        )

    async def test_external_mode_with_retries(self):
        mock_client = AsyncMock()
        mock_resp_500 = httpx.Response(500, request=httpx.Request("POST", "http://test"))
        mock_resp_200 = httpx.Response(
            200,
            json={"status": "confirmed", "app_id": "app_real_1"},
            request=httpx.Request("POST", "http://test"),
        )

        # First call fails with 500, second call succeeds
        mock_client.post.side_effect = [mock_resp_500, mock_resp_200]

        adapter = CorporateBankingAdapter(
            sandbox_mode=False,
            max_retries=2,
            base_backoff_seconds=0.01,
            client=mock_client,
        )

        package = BankingReadinessPackage(
            bank_partner_id="Emirates_NBD",
            kyc_kyb_checklist=["Trade License"],
            business_plan_markdown="# Corporate Banking Dossier Application",
            financial_projection_12m={"y1": 500000},
            readiness_score=89.0,
        )

        result = await adapter.submit_readiness_package(
            package, workspace_id="ws_real_001"
        )
        assert result["status"] == "confirmed"
        assert mock_client.post.call_count == 2
