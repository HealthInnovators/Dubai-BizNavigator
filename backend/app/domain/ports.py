"""Pure Clean Architecture domain ports (interfaces) for Dubai BizNavigator.

This module defines the abstract port protocols representing external boundaries.
All interfaces use standard `abc.ABC` and Python typing without depending on any
concrete database, agent runner, HTTP client, or observability SDK.

Concrete implementations reside strictly in `backend/app/infrastructure/`.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator
from typing import Any

from app.domain.entities import (
    BankingReadinessPackage,
    BusinessProfile,
    LicensingRecommendation,
    RegistrationPayload,
    RegulatoryAlert,
    StartupProfile,
)


class WorkspaceRepositoryPort(ABC):
    """Port for persisting and retrieving workspace artifacts, profiles, and alert states.

    Implemented by PostgreSQL adapters in production and in-memory mock repositories
    in unit tests.
    """

    # -----------------------------------------------------------------------
    # StartupProfile Operations
    # -----------------------------------------------------------------------

    @abstractmethod
    async def save_startup_profile(
        self, profile: StartupProfile, workspace_id: str
    ) -> StartupProfile:
        """Persist or update a StartupProfile entity for a given workspace.

        Args:
            profile: The validated StartupProfile domain entity.
            workspace_id: Unique identifier of the workspace partition.

        Returns:
            The persisted StartupProfile entity.
        """
        ...

    @abstractmethod
    async def get_startup_profile(self, workspace_id: str) -> StartupProfile | None:
        """Retrieve the StartupProfile associated with a workspace ID.

        Args:
            workspace_id: Unique workspace identifier.

        Returns:
            The StartupProfile if found, or None.
        """
        ...

    # -----------------------------------------------------------------------
    # LicensingRecommendation Operations
    # -----------------------------------------------------------------------

    @abstractmethod
    async def save_licensing_recommendation(
        self, recommendation: LicensingRecommendation, workspace_id: str
    ) -> LicensingRecommendation:
        """Persist or update a LicensingRecommendation entity.

        Args:
            recommendation: Scored recommendation entity.
            workspace_id: Unique workspace identifier.

        Returns:
            The persisted LicensingRecommendation entity.
        """
        ...

    @abstractmethod
    async def get_licensing_recommendation(
        self, workspace_id: str
    ) -> LicensingRecommendation | None:
        """Retrieve the active LicensingRecommendation for a workspace.

        Args:
            workspace_id: Unique workspace identifier.

        Returns:
            The LicensingRecommendation if exists, or None.
        """
        ...

    # -----------------------------------------------------------------------
    # RegistrationPayload Operations
    # -----------------------------------------------------------------------

    @abstractmethod
    async def save_registration_payload(
        self, payload: RegistrationPayload, workspace_id: str
    ) -> RegistrationPayload:
        """Persist or update a formal authority RegistrationPayload.

        Args:
            payload: The RegistrationPayload entity.
            workspace_id: Unique workspace identifier.

        Returns:
            The saved RegistrationPayload entity.
        """
        ...

    @abstractmethod
    async def get_registration_payload(
        self, workspace_id: str
    ) -> RegistrationPayload | None:
        """Retrieve the current RegistrationPayload for a workspace.

        Args:
            workspace_id: Unique workspace identifier.

        Returns:
            The RegistrationPayload if exists, or None.
        """
        ...

    # -----------------------------------------------------------------------
    # BankingReadinessPackage Operations
    # -----------------------------------------------------------------------

    @abstractmethod
    async def save_banking_readiness_package(
        self, package: BankingReadinessPackage, workspace_id: str
    ) -> BankingReadinessPackage:
        """Persist or update a BankingReadinessPackage dossier.

        Args:
            package: The BankingReadinessPackage entity.
            workspace_id: Unique workspace identifier.

        Returns:
            The persisted BankingReadinessPackage entity.
        """
        ...

    @abstractmethod
    async def get_banking_readiness_package(
        self, workspace_id: str
    ) -> BankingReadinessPackage | None:
        """Retrieve the BankingReadinessPackage for a workspace.

        Args:
            workspace_id: Unique workspace identifier.

        Returns:
            The BankingReadinessPackage if exists, or None.
        """
        ...

    # -----------------------------------------------------------------------
    # RegulatoryAlert & Source Hash Tracking Operations
    # -----------------------------------------------------------------------

    @abstractmethod
    async def save_regulatory_alert(self, alert: RegulatoryAlert) -> RegulatoryAlert:
        """Persist a newly detected RegulatoryAlert entity.

        Args:
            alert: The detected RegulatoryAlert entity.

        Returns:
            The saved RegulatoryAlert.
        """
        ...

    @abstractmethod
    async def get_regulatory_alerts(
        self, workspace_id: str | None = None
    ) -> list[RegulatoryAlert]:
        """Retrieve regulatory alerts, optionally filtered by workspace impact.

        Args:
            workspace_id: Optional workspace ID filter. If omitted, returns all alerts.

        Returns:
            List of matching RegulatoryAlert entities.
        """
        ...

    @abstractmethod
    async def get_all_startup_profiles(self) -> dict[str, StartupProfile]:
        """Retrieve all active workspace startup profiles across tenants.

        Returns:
            Dictionary mapping workspace_id -> StartupProfile entity.
        """
        ...

    @abstractmethod
    async def get_regulatory_hash(self, source_key: str) -> str | None:
        """Retrieve the last recorded SHA-256 content hash for a regulatory portal.

        Args:
            source_key: Unique key identifying the monitored government URL/gazette.

        Returns:
            The hex digest hash string if recorded, or None.
        """
        ...

    @abstractmethod
    async def set_regulatory_hash(self, source_key: str, content_hash: str) -> None:
        """Store the current SHA-256 content hash for a monitored regulatory portal.

        Args:
            source_key: Unique key identifying the monitored government URL/gazette.
            content_hash: Computed hexadecimal content hash string.
        """
        ...

    # -----------------------------------------------------------------------
    # Backwards Compatibility Operations
    # -----------------------------------------------------------------------

    @abstractmethod
    async def get_by_id(self, profile_id: str) -> BusinessProfile | None:
        """Fetch legacy business profile by ID.

        Args:
            profile_id: Profile UUID string.

        Returns:
            BusinessProfile entity if found, or None.
        """
        ...

    @abstractmethod
    async def save(self, profile: BusinessProfile) -> BusinessProfile:
        """Persist legacy business profile.

        Args:
            profile: The legacy BusinessProfile entity.

        Returns:
            The persisted BusinessProfile entity.
        """
        ...


class RegulatorySearchPort(ABC):
    """Port for querying official UAE licensing and regulatory authorities.

    Implemented by Tavily search adapters scoped strictly to verified government
    and free zone domains (dubaidet.gov.ae, investindubai.gov.ae, difc.com, dmcc.ae).
    """

    @abstractmethod
    async def search_regulatory_sources(
        self, query: str, jurisdiction: str | None = None
    ) -> list[dict[str, Any]]:
        """Search official UAE licensing sources returning structured snippets and verified URLs.

        Args:
            query: The natural language search query.
            jurisdiction: Optional authority filter (e.g. "DET", "DIFC", "DMCC").

        Returns:
            List of result dictionaries containing 'title', 'url', 'content', and 'score'.
        """
        ...


class BankingWorkflowPort(ABC):
    """Port for corporate banking partner workflows and Central Bank compliance.

    Implemented by HTTP client adapters communicating with UAE corporate banking gateways
    (e.g. Wio Bank, Emirates NBD) using idempotency keys and HMAC-SHA256 signature checks.
    """

    @abstractmethod
    async def fetch_kyc_checklist(
        self, bank_partner_id: str, licence_category: str
    ) -> list[str]:
        """Fetch tailored KYC/KYB checklist requirements for a specific bank partner.

        Args:
            bank_partner_id: Target banking partner code.
            licence_category: Statutory trade license category.

        Returns:
            List of requirement strings.
        """
        ...

    @abstractmethod
    async def submit_readiness_package(
        self, package: BankingReadinessPackage, workspace_id: str
    ) -> dict[str, Any]:
        """Submit banking readiness package to partner gateway.

        Enforces that human-in-the-loop approval has been granted prior to network dispatch.

        Args:
            package: The BankingReadinessPackage entity.
            workspace_id: Unique workspace identifier.

        Returns:
            Gateway response payload containing application ID and initial status.
        """
        ...

    @abstractmethod
    async def verify_webhook_signature(
        self, payload_bytes: bytes, signature: str, secret: str
    ) -> bool:
        """Verify HMAC-SHA256 signature on incoming banking partner webhooks.

        Args:
            payload_bytes: Raw HTTP request body bytes.
            signature: Signature header value from partner.
            secret: Shared HMAC cryptographic secret.

        Returns:
            True if signature matches, False otherwise.
        """
        ...

    @abstractmethod
    async def evaluate_eligibility(
        self,
        business_profile_id: str,
        jurisdiction_code: str,
        activity_code: str,
    ) -> dict[str, Any]:
        """Evaluate corporate bank account readiness against UAE banking guidelines.

        Args:
            business_profile_id: Profile identifier.
            jurisdiction_code: Code of incorporated jurisdiction.
            activity_code: Commercial activity classification code.

        Returns:
            Eligibility assessment dictionary with scores and flags.
        """
        ...


class ObservabilityPort(ABC):
    """Port for telemetry, multi-tenant trace isolation, and PII masking.

    Implemented by the Langfuse adapter using SDK v3+ with zero competing OTLP exporters.
    """

    @abstractmethod
    async def record_trace_metadata(
        self, trace_id: str, metadata: dict[str, Any]
    ) -> None:
        """Record metadata attributes on an active execution trace.

        Args:
            trace_id: Active trace identifier.
            metadata: Structured dictionary of metadata to append.
        """
        ...

    @abstractmethod
    async def flush(self) -> None:
        """Flush buffered spans, traces, and telemetry events to the collector."""
        ...


class AgentOrchestratorPort(ABC):
    """Port for autonomous setup workflows and Human-in-the-Loop pause/resume.

    Implemented by the DeepAgents / LangGraph orchestrator adapter.
    """

    @abstractmethod
    async def run_setup_workflow(
        self, profile: StartupProfile, workspace_id: str
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Run multi-agent setup workflow, streaming progress events and artifacts.

        Args:
            profile: The StartupProfile domain entity.
            workspace_id: Unique workspace identifier.

        Yields:
            Progress event dictionaries indicating subagent steps and artifact updates.
        """
        ...

    @abstractmethod
    async def resume_hitl_workflow(
        self, workspace_id: str, registration_payload: RegistrationPayload
    ) -> dict[str, Any]:
        """Resume setup workflow after Human-in-the-Loop decision confirmation.

        Args:
            workspace_id: Unique workspace identifier.
            registration_payload: Human-approved RegistrationPayload entity.

        Returns:
            Resumption result dictionary.
        """
        ...


# Legacy aliases for backwards compatibility
BusinessProfileRepositoryPort = WorkspaceRepositoryPort


class SearchServicePort(ABC):
    """Legacy search service port."""

    @abstractmethod
    async def search_regulations(
        self, query: str, jurisdiction: str | None = None
    ) -> list[dict[str, Any]]:
        ...


class BankingServicePort(ABC):
    """Legacy banking service port."""

    @abstractmethod
    async def evaluate_eligibility(
        self,
        business_profile_id: str,
        jurisdiction_code: str,
        activity_code: str,
    ) -> dict[str, Any]:
        ...
