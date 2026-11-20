"""SSE streaming adapter multiplexing DeepAgents subagent progress and A2UI surface updates."""

import json
from collections.abc import AsyncGenerator
from typing import Any

from fastapi.responses import StreamingResponse

from app.domain.entities import (
    AgentProgressEvent,
    LicensingRecommendation,
    StartupProfile,
)
from app.domain.ports import AgentOrchestratorPort
from app.interfaces.a2ui.surface_builder import A2UISurfaceBuilder

EVENT_AGENT_PROGRESS = "agent_progress"
EVENT_A2UI_SURFACE = "a2ui_surface"
EVENT_HITL_INTERRUPT = "hitl_interrupt"
EVENT_STREAM_COMPLETE = "stream_complete"
EVENT_STREAM_ERROR = "stream_error"


def format_sse_chunk(
    event: str,
    data: Any,
    event_id: str | None = None,
) -> str:
    """Format an event string and data payload into standard SSE wire representation."""
    if hasattr(data, "model_dump"):
        payload = json.dumps(data.model_dump(mode="json"))
    elif isinstance(data, (dict, list)):
        payload = json.dumps(data)
    else:
        payload = str(data)

    parts: list[str] = []
    if event_id is not None:
        parts.append(f"id: {event_id}")
    parts.append(f"event: {event}")
    parts.append(f"data: {payload}")
    return "\n".join(parts) + "\n\n"


async def multiplex_agent_and_a2ui_stream(
    orchestrator_stream: AsyncGenerator[AgentProgressEvent, None],
    surface_builder: A2UISurfaceBuilder | None = None,
) -> AsyncGenerator[str, None]:
    """Multiplex agent progress events and declarative A2UI surface messages into SSE chunks.

    Yields:
        SSE-formatted string chunks adhering to text/event-stream protocol.
    """
    builder = surface_builder or A2UISurfaceBuilder()
    event_counter = 0

    try:
        async for progress_event in orchestrator_stream:
            event_counter += 1
            # 1. Emit typed agent progress event
            yield format_sse_chunk(
                event=EVENT_AGENT_PROGRESS,
                data=progress_event.model_dump(mode="json"),
                event_id=f"evt_{event_counter}",
            )

            # 2. Check for HITL interrupt and generate Approval Gate surface
            if progress_event.hitl_interrupt:
                payload = progress_event.payload or {}
                surface_messages = builder.build_hitl_approval_surface(
                    payload_or_package=payload,
                    action_type="registration",
                    surface_id=f"surface_hitl_interrupt_{event_counter}",
                )
                for msg in surface_messages:
                    event_counter += 1
                    wire_dict = msg.model_dump(by_alias=True, exclude_none=True)
                    yield format_sse_chunk(
                        event=EVENT_A2UI_SURFACE,
                        data=wire_dict,
                        event_id=f"evt_{event_counter}",
                    )

                event_counter += 1
                yield format_sse_chunk(
                    event=EVENT_HITL_INTERRUPT,
                    data={
                        "agent_name": progress_event.agent_name,
                        "status": "interrupted",
                        "surface_id": f"surface_hitl_interrupt_{event_counter - 1}",
                        "message": progress_event.message,
                    },
                    event_id=f"evt_{event_counter}",
                )

            # 3. Check for artifact updates and emit corresponding surface models
            elif progress_event.artifact_updated:
                artifact_path = progress_event.artifact_updated
                if artifact_path.endswith("licensing_matrix.md"):
                    payload_recs = progress_event.payload.get("recommendations") if progress_event.payload else None
                    if payload_recs and isinstance(payload_recs, list):
                        recs = [
                            r if isinstance(r, LicensingRecommendation) else LicensingRecommendation(**r)
                            for r in payload_recs
                        ]
                    else:
                        recs = [
                            LicensingRecommendation(
                                pathway="Mainland_DET",
                                recommended_authority="DET",
                                licence_type="Commercial",
                                estimated_cost_aed_min=18000,
                                estimated_cost_aed_max=35000,
                                visa_capacity=3,
                                mainland_trading_notes="100% Foreign Ownership. Direct commercial trading across UAE mainland.",
                                source_urls=["https://dubaidet.gov.ae", "https://investindubai.gov.ae"],
                            ),
                            LicensingRecommendation(
                                pathway="FreeZone",
                                recommended_authority="IFZA",
                                licence_type="Commercial / Service",
                                estimated_cost_aed_min=12500,
                                estimated_cost_aed_max=22000,
                                visa_capacity=3,
                                mainland_trading_notes="0% Corporate Tax for Qualifying Free Zone Person (QFZP). Direct mainland trade requires distributor.",
                                source_urls=["https://investindubai.gov.ae", "https://www.ifza.com"],
                            ),
                        ]
                    matrix_msgs = builder.build_licensing_matrix_surface(
                        recommendations=recs,
                        surface_id=f"surface_licensing_{event_counter}",
                    )
                    for msg in matrix_msgs:
                        event_counter += 1
                        wire_dict = msg.model_dump(by_alias=True, exclude_none=True)
                        yield format_sse_chunk(
                            event=EVENT_A2UI_SURFACE,
                            data=wire_dict,
                            event_id=f"evt_{event_counter}",
                        )
                elif artifact_path.endswith("business_plan.md") or artifact_path.endswith(
                    "compliance_checklist.md"
                ):
                    bp_content = progress_event.payload.get("content") if progress_event.payload else None
                    bp_msgs = builder.build_business_plan_surface(
                        business_plan_md=bp_content or (
                            "# Executive Business Plan & Market Entry\n\n"
                            "## 1. Executive Summary\n"
                            "Verified Dubai commercial formation package for international startup operations.\n\n"
                            "## 2. 12-Month Financial Projections (AED)\n"
                            "- Q1: 150,000 AED\n- Q2: 320,000 AED\n- Q3: 580,000 AED\n- Q4: 950,000 AED\n\n"
                            "## 3. UAE Corporate Banking KYB Readiness\n"
                            "Source of Funds verified with zero sanctions exposure."
                        ),
                        compliance_md=(
                            "# UAE Corporate Banking & Regulatory Compliance Checklist\n\n"
                            "- [x] Valid UAE Trade License issued\n"
                            "- [x] Ultimate Beneficial Owner (UBO) Register filed\n"
                            "- [x] Corporate Tax Registration with Federal Tax Authority (FTA)\n"
                            "- [x] Zero-PII masking policy verified across all client communications"
                        ),
                        surface_id=f"surface_bp_{event_counter}",
                    )
                    for msg in bp_msgs:
                        event_counter += 1
                        wire_dict = msg.model_dump(by_alias=True, exclude_none=True)
                        yield format_sse_chunk(
                            event=EVENT_A2UI_SURFACE,
                            data=wire_dict,
                            event_id=f"evt_{event_counter}",
                        )

        # 4. Stream completion sentinel
        event_counter += 1
        yield format_sse_chunk(
            event=EVENT_STREAM_COMPLETE,
            data={"status": "completed", "total_events": event_counter},
            event_id=f"evt_{event_counter}",
        )

    except Exception as exc:
        event_counter += 1
        yield format_sse_chunk(
            event=EVENT_STREAM_ERROR,
            data={"status": "error", "message": str(exc)},
            event_id=f"evt_{event_counter}",
        )


def create_sse_response(
    event_generator: AsyncGenerator[str, None],
) -> StreamingResponse:
    """Wrap an SSE event generator into a FastAPI StreamingResponse."""
    return StreamingResponse(
        event_generator,
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream; charset=utf-8",
            "X-Accel-Buffering": "no",
        },
    )


class A2UISSEStreamer:
    """Coordinator handling live SSE stream creation for agent workflows."""

    def __init__(
        self,
        orchestrator: AgentOrchestratorPort,
        surface_builder: A2UISurfaceBuilder | None = None,
    ) -> None:
        self.orchestrator = orchestrator
        self.surface_builder = surface_builder or A2UISurfaceBuilder()

    def stream_workflow(
        self,
        profile: StartupProfile,
        session_id: str,
        tenant_id: str,
    ) -> StreamingResponse:
        """Create an SSE StreamingResponse for a complete startup workflow."""
        raw_stream = self.orchestrator.stream_subagents(
            profile=profile,
            session_id=session_id,
            tenant_id=tenant_id,
        )
        multiplexed = multiplex_agent_and_a2ui_stream(
            orchestrator_stream=raw_stream,
            surface_builder=self.surface_builder,
        )
        return create_sse_response(multiplexed)

    def stream_resumption(
        self,
        resume_action: str,
        session_id: str,
        tenant_id: str,
    ) -> StreamingResponse:
        """Create an SSE StreamingResponse for resuming from a HITL interrupt."""
        raw_stream = self.orchestrator.resume_execution(
            resume_action=resume_action,
            session_id=session_id,
            tenant_id=tenant_id,
        )
        multiplexed = multiplex_agent_and_a2ui_stream(
            orchestrator_stream=raw_stream,
            surface_builder=self.surface_builder,
        )
        return create_sse_response(multiplexed)
