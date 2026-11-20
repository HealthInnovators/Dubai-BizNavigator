"""Application use cases coordinating domain workflows, repository, and multi-agent orchestration."""

import logging
import uuid
from collections.abc import AsyncGenerator
from datetime import UTC, datetime
from typing import Any

from app.application.dtos.business_dto import (
    BusinessProfileResponseDTO,
    CreateBusinessProfileDTO,
)
from app.domain.entities import (
    BusinessProfile,
    RegistrationPayload,
    StartupProfile,
)
from app.domain.exceptions import (
    DomainValidationError,
)
from app.domain.ports import (
    AgentOrchestratorPort,
    BusinessProfileRepositoryPort,
    WorkspaceRepositoryPort,
)
from app.domain.value_objects.license_type import (
    Jurisdiction,
    JurisdictionType,
    LicenseCategory,
)
from app.interfaces.a2ui.sse_streamer import (
    EVENT_A2UI_SURFACE,
    EVENT_AGENT_PROGRESS,
    EVENT_STREAM_COMPLETE,
    format_sse_chunk,
    multiplex_agent_and_a2ui_stream,
)
from app.interfaces.a2ui.surface_builder import A2UISurfaceBuilder

logger = logging.getLogger("dubai_biznavigator.use_cases")


class InitializeBusinessProfileUseCase:
    """Orchestrates creation and validation of a legacy business formation profile."""

    def __init__(self, repository: BusinessProfileRepositoryPort) -> None:
        self.repository = repository

    async def execute(
        self, dto: CreateBusinessProfileDTO
    ) -> BusinessProfileResponseDTO:
        jurisdiction = Jurisdiction(
            name=dto.authority_code.upper(),
            jurisdiction_type=JurisdictionType(dto.jurisdiction_type),
            authority_code=dto.authority_code,
        )

        profile = BusinessProfile(
            business_name=dto.business_name,
            activity_description=dto.activity_description,
            license_category=LicenseCategory(dto.license_category),
            jurisdiction=jurisdiction,
        )
        profile.validate_for_submission()

        saved_profile = await self.repository.save(profile)

        return BusinessProfileResponseDTO(
            id=saved_profile.id,
            business_name=saved_profile.business_name,
            activity_description=saved_profile.activity_description,
            jurisdiction_type=saved_profile.jurisdiction.jurisdiction_type.value
            if saved_profile.jurisdiction
            else None,
            authority_code=saved_profile.jurisdiction.authority_code
            if saved_profile.jurisdiction
            else None,
            license_category=saved_profile.license_category.value
            if saved_profile.license_category
            else None,
            is_ready_for_application=saved_profile.is_ready_for_application,
            created_at=saved_profile.created_at.isoformat(),
        )


class StartSetupSessionUseCase:
    """Use case to initialize a new Dubai business setup workspace and user session."""

    def __init__(self, repository: WorkspaceRepositoryPort) -> None:
        self.repository = repository

    async def execute(
        self,
        profile_data: dict[str, Any] | StartupProfile | None = None,
        workspace_id: str | None = None,
        session_id: str | None = None,
        tenant_id: str = "default_tenant",
    ) -> dict[str, Any]:
        """Create session and workspace, persisting initial StartupProfile."""
        ws_id = workspace_id or f"ws_{uuid.uuid4().hex[:12]}"
        sess_id = session_id or f"sess_{uuid.uuid4().hex[:12]}"

        defaults = {
            "company_name": "Apex Global Technologies LLC",
            "industry_sector": "Technology",
            "business_activity": "Software Development and Technology Consulting",
            "revenue_model": "B2B_SaaS",
            "uae_local_trade": False,
            "visa_quota_needed": 3,
            "office_preference": "FlexiDesk",
            "founders_summary": "Setup Session initialized for Dubai incorporation.",
        }

        if isinstance(profile_data, StartupProfile):
            profile = profile_data
            profile.workspace_id = ws_id
        elif isinstance(profile_data, dict):
            merged = {**defaults, **profile_data}
            merged["workspace_id"] = ws_id
            profile = StartupProfile(**merged)
        else:
            defaults["workspace_id"] = ws_id
            profile = StartupProfile(**defaults)

        saved_profile = await self.repository.save_startup_profile(profile, ws_id)

        # Initialize pending registration payload in repository
        initial_registration = RegistrationPayload(
            workspace_id=ws_id,
            target_authority="DET",
            licence_category="Commercial",
            trade_name_candidates=[saved_profile.company_name],
            shareholding_structure=[{"name": "Founding Partner", "percentage": 100.0}],
            hitl_approved=False,
        )
        await self.repository.save_registration_payload(initial_registration, ws_id)

        return {
            "session_id": sess_id,
            "workspace_id": ws_id,
            "tenant_id": tenant_id,
            "status": "created",
            "created_at": datetime.now(UTC).isoformat(),
            "profile": saved_profile.model_dump(mode="json"),
        }


class ProcessUserMessageUseCase:
    """Use case to execute multi-agent coordination on user message and stream progress."""

    def __init__(
        self,
        orchestrator: AgentOrchestratorPort,
        repository: WorkspaceRepositoryPort,
        surface_builder: A2UISurfaceBuilder | None = None,
    ) -> None:
        self.orchestrator = orchestrator
        self.repository = repository
        self.surface_builder = surface_builder or A2UISurfaceBuilder()

    async def execute(
        self,
        session_id: str,
        message: str,
        workspace_id: str | None = None,
        tenant_id: str = "default_tenant",
    ) -> AsyncGenerator[str, None]:
        """Run agent workflow and stream progress + declarative A2UI surfaces."""
        ws_id = workspace_id or session_id
        profile = await self.repository.get_startup_profile(ws_id)

        if profile is None:
            profile = StartupProfile(
                workspace_id=ws_id,
                company_name="Apex Global Technologies LLC",
                industry_sector="Artificial Intelligence",
                business_activity="AI Consulting and Software Development",
                revenue_model="B2B_SaaS",
                uae_local_trade=True,
                visa_quota_needed=3,
                office_preference="PhysicalOffice",
                founders_summary=f"User prompted: {message}",
            )
            await self.repository.save_startup_profile(profile, ws_id)

        # Execute orchestration stream
        if hasattr(self.orchestrator, "stream_subagents"):
            agent_stream = self.orchestrator.stream_subagents(
                profile=profile,
                session_id=session_id,
                tenant_id=tenant_id,
            )
            async for chunk in multiplex_agent_and_a2ui_stream(
                orchestrator_stream=agent_stream,
                surface_builder=self.surface_builder,
            ):
                yield chunk
        else:
            # Fallback for generic AgentOrchestratorPort implementations
            raw_gen = self.orchestrator.run_setup_workflow(
                profile=profile,
                workspace_id=ws_id,
            )
            step_count = 0
            async for item in raw_gen:
                step_count += 1
                yield format_sse_chunk(
                    event=EVENT_AGENT_PROGRESS,
                    data={"step": step_count, "data": item},
                    event_id=f"evt_{step_count}",
                )
            yield format_sse_chunk(
                event=EVENT_STREAM_COMPLETE,
                data={"status": "completed"},
                event_id=f"evt_{step_count + 1}",
            )


class ApproveHITLGateUseCase:
    """Use case to validate Human-in-the-Loop decision and resume execution."""

    def __init__(
        self,
        orchestrator: AgentOrchestratorPort,
        repository: WorkspaceRepositoryPort,
        surface_builder: A2UISurfaceBuilder | None = None,
    ) -> None:
        self.orchestrator = orchestrator
        self.repository = repository
        self.surface_builder = surface_builder or A2UISurfaceBuilder()

    async def execute(
        self,
        session_id: str,
        action: str = "hitl_approve",
        workspace_id: str | None = None,
        tenant_id: str = "default_tenant",
        payload_updates: dict[str, Any] | None = None,
    ) -> AsyncGenerator[str, None]:
        """Validate approval, update repository, and resume LangGraph checkpointer."""
        if action not in ("hitl_approve", "hitl_reject"):
            raise DomainValidationError(
                f"Invalid HITL action '{action}'. Must be 'hitl_approve' or 'hitl_reject'."
            )

        ws_id = workspace_id or session_id
        reg_payload = await self.repository.get_registration_payload(ws_id)

        if reg_payload is None:
            reg_payload = RegistrationPayload(
                workspace_id=ws_id,
                target_authority="DET",
                licence_category="Commercial",
                trade_name_candidates=["Acme Tech LLC"],
                shareholding_structure=[{"name": "Founder", "percentage": 100.0}],
            )

        if action == "hitl_approve":
            reg_payload.hitl_approved = True
            reg_payload.approved_at = datetime.now(UTC)
            if payload_updates:
                if "target_authority" in payload_updates:
                    reg_payload.target_authority = payload_updates["target_authority"]
                if "licence_category" in payload_updates:
                    reg_payload.licence_category = payload_updates["licence_category"]
            await self.repository.save_registration_payload(reg_payload, ws_id)

        # Resume orchestrator execution
        if hasattr(self.orchestrator, "resume_execution"):
            resume_stream = self.orchestrator.resume_execution(
                resume_action=action,
                session_id=session_id,
                tenant_id=tenant_id,
            )
            async for chunk in multiplex_agent_and_a2ui_stream(
                orchestrator_stream=resume_stream,
                surface_builder=self.surface_builder,
            ):
                yield chunk
        else:
            # Fallback for generic AgentOrchestratorPort implementations
            res = await self.orchestrator.resume_hitl_workflow(
                workspace_id=ws_id,
                registration_payload=reg_payload,
            )
            yield format_sse_chunk(
                event=EVENT_A2UI_SURFACE,
                data={"status": "resumed", "result": res},
                event_id="evt_resume_1",
            )
            yield format_sse_chunk(
                event=EVENT_STREAM_COMPLETE,
                data={"status": "completed"},
                event_id="evt_resume_2",
            )


class GetWorkspaceArtifactsUseCase:
    """Use case to gather all generated structured and markdown artifacts for a workspace."""

    def __init__(self, repository: WorkspaceRepositoryPort) -> None:
        self.repository = repository

    async def execute(self, workspace_id: str) -> dict[str, Any]:
        """Retrieve complete package of workspace artifacts."""
        profile = await self.repository.get_startup_profile(workspace_id)
        recommendation = await self.repository.get_licensing_recommendation(workspace_id)
        registration = await self.repository.get_registration_payload(workspace_id)
        banking_package = await self.repository.get_banking_readiness_package(
            workspace_id
        )

        company_name = profile.company_name if profile else workspace_id

        # Render canonical virtual workspace markdown representations
        licensing_markdown = (
            f"# Dubai Licensing Matrix & Jurisdiction Analysis\n\n"
            f"**Company**: {company_name}\n"
            f"**Recommended Authority**: {recommendation.recommended_authority if recommendation else 'DET'}\n"
            f"**Pathway**: {recommendation.pathway if recommendation else 'Mainland_DET'}\n"
            f"**Cost Range**: AED {recommendation.estimated_cost_aed_min:,} - {recommendation.estimated_cost_aed_max:,}\n"
            if recommendation
            else "# Dubai Licensing Matrix\nAnalysis in progress..."
        )

        business_plan_markdown = (
            banking_package.business_plan_markdown
            if banking_package
            else (
                f"# Executive Business Plan: {company_name}\n\n"
                "## 1. Executive Summary\n"
                "Dubai market expansion and commercial strategy.\n"
            )
        )

        checklist_items = (
            banking_package.kyc_kyb_checklist
            if banking_package
            else [
                "Valid UAE Trade License Copy",
                "Certificate of Incorporation",
                "Shareholder Passports and Emirates IDs",
                "Proof of Business Address (Ejari)",
            ]
        )
        compliance_markdown = (
            "# UAE Corporate Banking KYB / KYC Compliance Checklist\n\n"
            + "\n".join([f"- [x] {item}" for item in checklist_items])
        )

        return {
            "workspace_id": workspace_id,
            "artifacts": {
                "startup_profile": profile.model_dump(mode="json") if profile else None,
                "licensing_recommendation": (
                    recommendation.model_dump(mode="json") if recommendation else None
                ),
                "registration_payload": (
                    registration.model_dump(mode="json") if registration else None
                ),
                "banking_readiness_package": (
                    banking_package.model_dump(mode="json")
                    if banking_package
                    else None
                ),
            },
            "workspace_files": {
                "/workspace/startup_profile.json": (
                    profile.model_dump_json(indent=2) if profile else "{}"
                ),
                "/workspace/licensing_matrix.md": licensing_markdown,
                "/workspace/registration_payload.json": (
                    registration.model_dump_json(indent=2) if registration else "{}"
                ),
                "/workspace/business_plan.md": business_plan_markdown,
                "/workspace/compliance_checklist.md": compliance_markdown,
            },
        }
