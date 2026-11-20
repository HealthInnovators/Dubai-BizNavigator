"""FastAPI REST and SSE routes for session management, agent workflow, and banking webhooks."""

import json
import logging
from typing import Any, Literal

from fastapi import (
    APIRouter,
    Depends,
    Header,
    HTTPException,
    Request,
    status,
)
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.interfaces.a2ui.sse_streamer import create_sse_response
from app.interfaces.container import Container, get_container

logger = logging.getLogger("dubai_biznavigator.api")

router = APIRouter(tags=["BizNavigator Sessions & Workflow"])


class CreateSessionRequest(BaseModel):
    """Payload to initialize a new setup workspace and session."""

    company_name: str | None = None
    industry_sector: str | None = None
    business_activity: str | None = None
    revenue_model: str | None = None
    uae_local_trade: bool | None = None
    visa_quota_needed: int | None = Field(default=None, ge=0)
    office_preference: str | None = None
    founders_summary: str | None = None
    tenant_id: str = "default_tenant"


class UserMessageRequest(BaseModel):
    """Payload to send user intent or instruction to the orchestration agent."""

    message: str = Field(..., min_length=1)
    workspace_id: str | None = None
    tenant_id: str = "default_tenant"


class HITLApproveRequest(BaseModel):
    """Payload for Human-in-the-Loop approval gate resolution."""

    action: Literal["hitl_approve", "hitl_reject"] = "hitl_approve"
    workspace_id: str | None = None
    tenant_id: str = "default_tenant"
    payload_updates: dict[str, Any] | None = None


@router.post("/v1/sessions", status_code=status.HTTP_201_CREATED)
async def create_setup_session(
    payload: CreateSessionRequest | None = None,
    container: Container = Depends(get_container),
) -> dict[str, Any]:
    """Create a new business formation workspace and interactive session."""
    data = payload.model_dump(exclude_none=True) if payload else {}
    tenant_id = data.pop("tenant_id", "default_tenant")
    return await container.start_session_use_case.execute(
        profile_data=data if data else None,
        tenant_id=tenant_id,
    )


@router.post("/v1/sessions/{session_id}/messages")
async def send_session_message(
    session_id: str,
    payload: UserMessageRequest,
    container: Container = Depends(get_container),
) -> StreamingResponse:
    """Run agent workflow and stream progress events + declarative A2UI surfaces (SSE)."""
    event_stream = container.process_message_use_case.execute(
        session_id=session_id,
        message=payload.message,
        workspace_id=payload.workspace_id,
        tenant_id=payload.tenant_id,
    )
    return create_sse_response(event_stream)


@router.post("/v1/sessions/{session_id}/approve")
async def approve_hitl_gate(
    session_id: str,
    payload: HITLApproveRequest,
    container: Container = Depends(get_container),
) -> StreamingResponse:
    """Validate HITL confirmation and resume LangGraph durable checkpointer."""
    resume_stream = container.approve_hitl_use_case.execute(
        session_id=session_id,
        action=payload.action,
        workspace_id=payload.workspace_id,
        tenant_id=payload.tenant_id,
        payload_updates=payload.payload_updates,
    )
    return create_sse_response(resume_stream)


@router.get("/v1/workspaces/{workspace_id}/artifacts")
async def get_workspace_artifacts(
    workspace_id: str,
    container: Container = Depends(get_container),
) -> dict[str, Any]:
    """Retrieve all generated structured and markdown artifacts for a workspace."""
    return await container.get_artifacts_use_case.execute(workspace_id=workspace_id)


@router.get("/v1/workspaces/{workspace_id}/alerts")
async def get_workspace_alerts(
    workspace_id: str,
    container: Container = Depends(get_container),
) -> dict[str, Any]:
    """Retrieve regulatory compliance alerts for a workspace and emit A2UI Alert Banner surface."""
    alerts = await container.repository.get_regulatory_alerts(workspace_id)

    a2ui_surface: list[dict[str, Any]] = []
    if alerts:
        surface_messages = container.surface_builder.build_regulatory_alert_surface(
            alerts=alerts,
            surface_id=f"surface_alerts_{workspace_id}",
        )
        a2ui_surface = container.surface_builder.to_wire_dicts(surface_messages)

    return {
        "workspace_id": workspace_id,
        "alert_count": len(alerts),
        "alerts": [alert.model_dump(mode="json") for alert in alerts],
        "a2ui_surface": a2ui_surface,
    }


@router.post("/v1/webhooks/banking", status_code=status.HTTP_200_OK)
async def receive_banking_webhook(
    request: Request,
    x_banking_signature: str | None = Header(None, alias="X-Banking-Signature"),
    x_hub_signature_256: str | None = Header(None, alias="X-Hub-Signature-256"),
    x_signature: str | None = Header(None, alias="X-Signature"),
    container: Container = Depends(get_container),
) -> dict[str, Any]:
    """Receive asynchronous corporate banking KYC status updates with HMAC verification."""
    signature = x_banking_signature or x_hub_signature_256 or x_signature
    if not signature:
        logger.warning("Banking webhook rejected: Missing signature header.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing signature header (X-Banking-Signature).",
        )

    raw_body = await request.body()
    secret = container.settings.BANKING_WEBHOOK_SECRET

    is_valid = await container.corporate_banking.verify_webhook_signature(
        payload_bytes=raw_body,
        signature=signature,
        secret=secret,
    )

    if not is_valid:
        logger.warning("Banking webhook rejected: Invalid HMAC-SHA256 signature.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid HMAC-SHA256 signature.",
        )

    try:
        payload = json.loads(raw_body.decode("utf-8")) if raw_body else {}
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Malformed JSON payload: {exc}",
        ) from exc

    event_type = payload.get("event", "kyc.status_updated")
    event_id = payload.get("event_id", payload.get("id"))
    application_id = payload.get("application_id", payload.get("submission_id"))

    logger.info(
        "Banking webhook verified successfully: %s (App ID: %s)",
        event_type,
        application_id,
    )

    return {
        "status": "received",
        "event": event_type,
        "event_id": event_id,
        "application_id": application_id,
    }
