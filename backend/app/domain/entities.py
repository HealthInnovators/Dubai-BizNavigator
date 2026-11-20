"""Pure Clean Architecture domain entities for Dubai BizNavigator.

This module houses the core enterprise business entities, invariants, and validation rules.
In accordance with Clean Architecture principles:
- Zero third-party runtime dependencies on web frameworks (FastAPI, Starlette).
- Zero dependencies on agent orchestration frameworks (LangChain, LangGraph, DeepAgents).
- Zero dependencies on telemetry or UI libraries (Langfuse, A2UI).
- Validated via Pydantic v2 schemas and strict custom validators.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.domain.exceptions import (
    BusinessRuleViolationError,
    DomainValidationError,
    HITLApprovalRequiredError,
)
from app.domain.value_objects.license_type import Jurisdiction, LicenseCategory


class StartupProfile(BaseModel):
    """Core domain entity encapsulating a business's formation parameters in Dubai.

    Attributes:
        id: Unique UUID string identifying this profile.
        workspace_id: Associated virtual workspace partition identifier.
        company_name: Proposed trade/legal name for the entity.
        industry_sector: Broad commercial vertical (e.g. Technology, FinTech, Commodities).
        business_activity: Granular commercial activities matching UAE ISIC-4 registry.
        revenue_model: Commercial monetization architecture (B2B SaaS, E-Commerce, etc.).
        uae_local_trade: Whether direct onshore commercial contracting is required in mainland UAE.
        visa_quota_needed: Number of investor, partner, and employee residence visas required.
        office_preference: Physical office requirements (FlexiDesk, PhysicalOffice, Warehousing, None).
        founders_summary: Biographical, nationality, and residency summary of founding partners.
        created_at: ISO UTC timestamp marking entity instantiation.

    Invariants:
        - `company_name`, `business_activity`, and `industry_sector` must be non-empty strings.
        - `visa_quota_needed` must be a non-negative integer.
    """

    model_config = ConfigDict(extra="ignore")

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    workspace_id: str | None = None
    company_name: str = Field(..., min_length=2, max_length=150)
    industry_sector: str = Field(..., min_length=2, max_length=100)
    business_activity: str = Field(..., min_length=3, max_length=500)
    revenue_model: str = Field(..., min_length=3, max_length=200)
    uae_local_trade: bool = False
    visa_quota_needed: int = Field(default=1, ge=0)
    office_preference: str = Field(..., min_length=2, max_length=100)
    founders_summary: str = Field(..., min_length=5)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @field_validator("company_name", "business_activity", "industry_sector")
    @classmethod
    def validate_non_empty_strings(cls, v: str) -> str:
        """Ensure string fields contain non-whitespace text.

        Args:
            v: Raw string value to inspect.

        Returns:
            Trimmed string value.

        Raises:
            DomainValidationError: If input is empty or pure whitespace.
        """
        if not v or not v.strip():
            raise DomainValidationError("String field must not be empty or whitespace.")
        return v.strip()

    @field_validator("visa_quota_needed")
    @classmethod
    def validate_visa_quota(cls, v: int) -> int:
        """Enforce non-negative residence visa capacity requirement.

        Args:
            v: Requested visa count.

        Returns:
            Validated non-negative integer.

        Raises:
            DomainValidationError: If visa count is less than 0.
        """
        if v < 0:
            raise DomainValidationError("visa_quota_needed cannot be negative.")
        return v


class LicensingRecommendation(BaseModel):
    """Domain entity representing evaluated licensing pathway guidance.

    Produced by the `licensing-strategist` subagent after comparative analysis between
    Dubai Mainland (Department of Economy and Tourism - DET) and UAE Free Zones.

    Attributes:
        id: Unique identifier for this recommendation instance.
        workspace_id: Bound workspace identifier.
        pathway: Primary jurisdiction pathway ("Mainland_DET" vs "FreeZone").
        recommended_authority: Designated licensing authority (e.g. "DET", "DIFC", "DMCC", "IFZA").
        licence_type: Classification of the trade license (Commercial, Professional, Industrial, etc.).
        estimated_cost_aed_min: Lower bound of estimated total establishment fees in AED.
        estimated_cost_aed_max: Upper bound of estimated total establishment fees in AED.
        visa_capacity: Number of residence visas supported under the recommended package.
        mainland_trading_notes: Legal operational notes regarding domestic UAE market access.
        source_urls: Authoritative official URLs grounding the recommendation.
        created_at: ISO UTC timestamp marking recommendation creation.

    Invariants:
        - `estimated_cost_aed_max` must be greater than or equal to `estimated_cost_aed_min`.
        - `source_urls` must contain at least one non-empty official citation URL.
    """

    model_config = ConfigDict(extra="ignore")

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    workspace_id: str | None = None
    pathway: Literal["Mainland_DET", "FreeZone"]
    recommended_authority: str = Field(..., min_length=2)
    licence_type: str = Field(..., min_length=2)
    estimated_cost_aed_min: float = Field(..., ge=0.0)
    estimated_cost_aed_max: float = Field(..., ge=0.0)
    visa_capacity: int = Field(default=1, ge=0)
    mainland_trading_notes: str = ""
    source_urls: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @field_validator("source_urls")
    @classmethod
    def validate_source_urls(cls, v: list[str]) -> list[str]:
        """Validate that citations are non-empty and non-blank.

        Args:
            v: List of candidate URLs.

        Returns:
            Cleaned list of trimmed URLs.

        Raises:
            DomainValidationError: If list is empty or contains whitespace-only strings.
        """
        if not v:
            raise DomainValidationError(
                "source_urls cannot be empty on LicensingRecommendation."
            )
        cleaned: list[str] = []
        for url in v:
            trimmed = url.strip()
            if not trimmed:
                raise DomainValidationError("source_urls cannot contain empty entries.")
            cleaned.append(trimmed)
        return cleaned

    @model_validator(mode="after")
    def validate_cost_bounds(self) -> LicensingRecommendation:
        """Enforce fee estimation bounds consistency.

        Returns:
            The validated LicensingRecommendation instance.

        Raises:
            DomainValidationError: If max cost is less than min cost.
        """
        if self.estimated_cost_aed_max < self.estimated_cost_aed_min:
            raise DomainValidationError(
                f"estimated_cost_aed_max ({self.estimated_cost_aed_max}) cannot be less than "
                f"estimated_cost_aed_min ({self.estimated_cost_aed_min})."
            )
        return self


class RegistrationPayload(BaseModel):
    """Domain entity representing a formalized trade license application payload.

    Acts as the primary Human-in-the-Loop (HITL) gatekeeper entity: external submission
    is strictly forbidden until `hitl_approved` is confirmed by the human user.

    Attributes:
        id: Unique identifier for the registration payload.
        workspace_id: Associated workspace ID.
        target_authority: Legal body targeted (e.g. DET, DIFC, DMCC).
        licence_category: Statutory classification.
        trade_name_candidates: Ranked list of proposed business names for reservation.
        shareholding_structure: Breakdown of partner equity and citizenship percentages.
        hitl_approved: Boolean gate flag indicating human confirmation.
        approved_at: Timestamp when human user confirmed the filing.
        submitted_at: Timestamp when external authority dispatch occurred.
    """

    model_config = ConfigDict(extra="ignore")

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    workspace_id: str | None = None
    target_authority: str = Field(..., min_length=2)
    licence_category: str = Field(..., min_length=2)
    trade_name_candidates: list[str] = Field(default_factory=list)
    shareholding_structure: list[dict[str, Any]] = Field(default_factory=list)
    hitl_approved: bool = False
    approved_at: datetime | None = None
    submitted_at: datetime | None = None

    @field_validator("trade_name_candidates")
    @classmethod
    def validate_trade_names(cls, v: list[str]) -> list[str]:
        """Verify that at least one candidate trade name is provided.

        Args:
            v: List of proposed names.

        Returns:
            Validated list of names.

        Raises:
            DomainValidationError: If list is empty or entries are blank.
        """
        if not v:
            raise DomainValidationError("At least one trade_name_candidate must be provided.")
        for name in v:
            if not name.strip():
                raise DomainValidationError("Trade name candidate cannot be empty.")
        return v

    def approve_hitl(self) -> None:
        """Mark payload as approved by Human-in-the-Loop decision gate.

        Sets `hitl_approved` to True and records the approval timestamp in UTC.
        """
        self.hitl_approved = True
        self.approved_at = datetime.now(UTC)

    def ensure_hitl_approved(self) -> None:
        """Enforce that Human-in-the-Loop approval has been granted before external dispatch.

        Raises:
            HITLApprovalRequiredError: If `hitl_approved` is False.
        """
        if not self.hitl_approved:
            raise HITLApprovalRequiredError(
                "Operation requires Human-In-The-Loop approval before proceeding with registration."
            )


class BankingReadinessPackage(BaseModel):
    """Domain entity representing a corporate banking KYB/KYC dossier.

    Contains financial models, executive business plans, and compliance checklists
    formatted for transmission to UAE commercial banking partners (e.g. Wio Bank, Emirates NBD).

    Attributes:
        id: Unique dossier identifier.
        workspace_id: Associated workspace identifier.
        bank_partner_id: Identifier of target corporate bank.
        kyc_kyb_checklist: Verified checklist items (UBO, Trade License, Ejari, Bank Statements).
        business_plan_markdown: Full executive business plan and source of funds narrative.
        financial_projection_12m: 12-month revenue, expense, and cash runway projections.
        readiness_score: Composite readiness score between 0.0 and 100.0.
        created_at: ISO UTC timestamp marking package compilation.
    """

    model_config = ConfigDict(extra="ignore")

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    workspace_id: str | None = None
    bank_partner_id: str = Field(..., min_length=2)
    kyc_kyb_checklist: list[str] = Field(default_factory=list)
    business_plan_markdown: str = Field(..., min_length=10)
    financial_projection_12m: dict[str, Any] = Field(default_factory=dict)
    readiness_score: float = Field(..., ge=0.0, le=100.0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @field_validator("readiness_score")
    @classmethod
    def validate_score(cls, v: float) -> float:
        """Validate composite banking readiness score scale.

        Args:
            v: Numerical score value.

        Returns:
            Validated float within [0.0, 100.0].

        Raises:
            DomainValidationError: If score is out of bounds.
        """
        if v < 0.0 or v > 100.0:
            raise DomainValidationError("readiness_score must be between 0.0 and 100.0.")
        return v


class RegulatoryAlert(BaseModel):
    """Domain entity representing a detected legal, tax, or licensing rule change in the UAE.

    Generated by the scheduled `RegulatoryUpdateMonitor` service when an official gazette
    ruling or portal update diverges from stored workspace baseline hashes.

    Attributes:
        alert_id: Unique alert hash identifier.
        authority: Government authority issuing update (e.g. "DET", "FTA", "CBUAE", "DFSA").
        change_summary: Plaintext summary of the regulatory mutation.
        effective_date: Date when the rule enters into legal force.
        source_url: Official gazette or cabinet resolution link.
        impacted_workspace_ids: List of workspace IDs whose jurisdiction/activities are affected.
        created_at: ISO UTC timestamp when alert was detected.
    """

    model_config = ConfigDict(extra="ignore")

    alert_id: str = Field(..., min_length=2)
    authority: str = Field(..., min_length=2)
    change_summary: str = Field(..., min_length=5)
    effective_date: str = Field(..., min_length=4)
    source_url: str = Field(..., min_length=4)
    impacted_workspace_ids: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @field_validator("source_url", mode="before")
    @classmethod
    def validate_url(cls, v: Any) -> str:
        """Validate non-empty source URL.

        Args:
            v: Input source URL string.

        Returns:
            Trimmed URL string.

        Raises:
            DomainValidationError: If input is empty or non-string.
        """
        if not isinstance(v, str) or not v.strip():
            raise DomainValidationError("source_url must not be empty.")
        return v.strip()


class AgentProgressEvent(BaseModel):
    """Typed domain progress event yielded during orchestrator workflow execution.

    Multiplexed across Server-Sent Events (SSE) to update the frontend timeline
    and notify clients of subagent transitions, tool calls, and virtual file modifications.

    Attributes:
        agent_name: Name of active subagent (e.g. "licensing-strategist", "form-automation-agent").
        status: Current state ("started", "running", "completed", "interrupted", "failed").
        tool_call: Metadata dictionary detailing active tool invocation and parameters.
        artifact_updated: Virtual filesystem path of modified artifact (e.g. "/workspace/licensing_matrix.md").
        hitl_interrupt: Boolean flag indicating LangGraph checkpointer paused at a decision gate.
        message: Human-readable narrative describing current subagent thought or action.
        payload: Arbitrary structured data attached to the event.
    """

    model_config = ConfigDict(extra="ignore")

    agent_name: str
    status: str = "running"
    tool_call: dict[str, Any] | None = None
    artifact_updated: str | None = None
    hitl_interrupt: bool = False
    message: str = ""
    payload: dict[str, Any] = Field(default_factory=dict)


class BusinessProfile(BaseModel):
    """BusinessProfile entity maintained for backwards compatibility with early endpoints."""

    model_config = ConfigDict(extra="ignore", arbitrary_types_allowed=True)

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    business_name: str = ""
    activity_description: str = ""
    license_category: LicenseCategory | None = None
    jurisdiction: Jurisdiction | None = None
    target_launch_date: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    is_ready_for_application: bool = False

    def validate_for_submission(self) -> None:
        """Validate that mandatory Dubai incorporation fields are populated.

        Raises:
            BusinessRuleViolationError: If business name, activity, jurisdiction, or license category are missing.
        """
        if not self.business_name.strip():
            raise BusinessRuleViolationError("Business name must not be empty.")
        if not self.activity_description.strip():
            raise BusinessRuleViolationError("Activity description must not be empty.")
        if self.jurisdiction is None:
            raise BusinessRuleViolationError("A valid Dubai jurisdiction must be selected.")
        if self.license_category is None:
            raise BusinessRuleViolationError("A license category must be selected.")
        self.is_ready_for_application = True
