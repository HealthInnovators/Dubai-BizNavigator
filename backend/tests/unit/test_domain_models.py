"""Comprehensive unit tests for pure domain models and validation rules.

Verifies domain entities, value objects, exceptions, and port contracts
with zero framework dependencies.
"""

import pytest
from pydantic import ValidationError

from app.domain.entities import (
    BankingReadinessPackage,
    LicensingRecommendation,
    RegistrationPayload,
    RegulatoryAlert,
    StartupProfile,
)
from app.domain.exceptions import (
    DomainError,
    DomainValidationError,
    ExternalIntegrationError,
    HITLApprovalRequiredError,
    JurisdictionConflictError,
)
from app.domain.ports import (
    AgentOrchestratorPort,
    BankingWorkflowPort,
    ObservabilityPort,
    RegulatorySearchPort,
    WorkspaceRepositoryPort,
)


class TestStartupProfile:
    """Tests for StartupProfile entity."""

    def test_valid_startup_profile_creation(self) -> None:
        profile = StartupProfile(
            company_name="Apex Global Tech",
            industry_sector="Information Technology",
            business_activity="Cloud Consulting and AI Solutions",
            revenue_model="SaaS and Professional Services",
            uae_local_trade=False,
            visa_quota_needed=3,
            office_preference="flexi_desk",
            founders_summary="Two technical founders with 10+ years experience in enterprise AI.",
        )
        assert profile.company_name == "Apex Global Tech"
        assert profile.visa_quota_needed == 3
        assert profile.uae_local_trade is False
        assert profile.id is not None
        assert profile.created_at is not None

    def test_company_name_cannot_be_empty(self) -> None:
        with pytest.raises(DomainValidationError):
            StartupProfile(
                company_name="   ",
                industry_sector="Tech",
                business_activity="Consulting",
                revenue_model="SaaS",
                office_preference="flexi",
                founders_summary="Founder profile",
            )

    def test_negative_visa_quota_rejected(self) -> None:
        with pytest.raises((DomainValidationError, ValidationError)):
            StartupProfile(
                company_name="Apex Global Tech",
                industry_sector="Tech",
                business_activity="Consulting",
                revenue_model="SaaS",
                visa_quota_needed=-2,
                office_preference="flexi",
                founders_summary="Founder profile",
            )


class TestLicensingRecommendation:
    """Tests for LicensingRecommendation entity and validation rules."""

    def test_valid_licensing_recommendation(self) -> None:
        rec = LicensingRecommendation(
            pathway="FreeZone",
            recommended_authority="IFZA",
            licence_type="Commercial",
            estimated_cost_aed_min=14500.0,
            estimated_cost_aed_max=19500.0,
            visa_capacity=2,
            mainland_trading_notes="Requires mainland service agent or branch for onshore sales.",
            source_urls=[
                "https://www.ifza.com/en/licensing",
                "https://ded.dubai.gov.ae/regulations",
            ],
        )
        assert rec.pathway == "FreeZone"
        assert rec.recommended_authority == "IFZA"
        assert rec.estimated_cost_aed_min == 14500.0
        assert len(rec.source_urls) == 2

    def test_source_urls_cannot_be_empty(self) -> None:
        """Verify validation rule: source_urls cannot be empty on LicensingRecommendation."""
        with pytest.raises(DomainValidationError, match="source_urls cannot be empty"):
            LicensingRecommendation(
                pathway="FreeZone",
                recommended_authority="DMCC",
                licence_type="Trading",
                estimated_cost_aed_min=25000.0,
                estimated_cost_aed_max=35000.0,
                source_urls=[],
            )

    def test_source_urls_cannot_contain_empty_strings(self) -> None:
        with pytest.raises(DomainValidationError, match="source_urls cannot contain empty"):
            LicensingRecommendation(
                pathway="Mainland_DET",
                recommended_authority="DET",
                licence_type="Commercial",
                estimated_cost_aed_min=18000.0,
                estimated_cost_aed_max=25000.0,
                source_urls=["   "],
            )

    def test_cost_max_less_than_min_raises_error(self) -> None:
        """Verify estimated_cost_aed_max cannot be strictly less than estimated_cost_aed_min."""
        with pytest.raises(DomainValidationError, match="cannot be less than"):
            LicensingRecommendation(
                pathway="Mainland_DET",
                recommended_authority="DET",
                licence_type="Commercial",
                estimated_cost_aed_min=20000.0,
                estimated_cost_aed_max=15000.0,
                source_urls=["https://ded.dubai.gov.ae"],
            )


class TestRegistrationPayload:
    """Tests for RegistrationPayload entity and HITL approval workflow."""

    def test_hitl_approved_defaults_to_false(self) -> None:
        """Verify validation rule: hitl_approved defaults to False."""
        payload = RegistrationPayload(
            target_authority="IFZA",
            licence_category="Commercial",
            trade_name_candidates=["Apex Cloud FZ-LLC", "Apex Tech Solutions"],
        )
        assert payload.hitl_approved is False
        assert payload.approved_at is None

    def test_ensure_hitl_approved_raises_error_when_false(self) -> None:
        """Verify ensure_hitl_approved raises HITLApprovalRequiredError if not approved."""
        payload = RegistrationPayload(
            target_authority="DET",
            licence_category="Professional",
            trade_name_candidates=["Falcon Innovations LLC"],
        )
        with pytest.raises(HITLApprovalRequiredError, match="Human-In-The-Loop approval"):
            payload.ensure_hitl_approved()

    def test_approve_hitl_flow(self) -> None:
        """Verify approving HITL updates state and allows execution to proceed."""
        payload = RegistrationPayload(
            target_authority="DIFC",
            licence_category="Financial",
            trade_name_candidates=["Emirates AI Capital Ltd"],
        )
        assert payload.hitl_approved is False
        payload.approve_hitl()
        assert payload.hitl_approved is True
        assert payload.approved_at is not None
        # Should now pass without raising
        payload.ensure_hitl_approved()

    def test_empty_trade_name_candidates_raises_error(self) -> None:
        with pytest.raises(DomainValidationError, match="At least one trade_name_candidate"):
            RegistrationPayload(
                target_authority="DET",
                licence_category="Commercial",
                trade_name_candidates=[],
            )


class TestBankingReadinessPackage:
    """Tests for BankingReadinessPackage entity and score validation."""

    def test_valid_banking_readiness_package(self) -> None:
        package = BankingReadinessPackage(
            bank_partner_id="wio_business",
            kyc_kyb_checklist=[
                "Trade License Certificate",
                "Shareholder Passport Copies",
                "Emirates ID of General Manager",
            ],
            business_plan_markdown="# Business Plan\nComprehensive 3-year operations outline.",
            financial_projection_12m={"m1_burn": 10000, "m12_revenue": 50000},
            readiness_score=88.5,
        )
        assert package.bank_partner_id == "wio_business"
        assert package.readiness_score == 88.5
        assert len(package.kyc_kyb_checklist) == 3

    def test_readiness_score_out_of_bounds_raises_error(self) -> None:
        with pytest.raises((DomainValidationError, ValidationError)):
            BankingReadinessPackage(
                bank_partner_id="mashreq_neobiz",
                kyc_kyb_checklist=["MOA"],
                business_plan_markdown="# Plan\nValid details here.",
                financial_projection_12m={},
                readiness_score=105.0,  # Invalid: > 100.0
            )

        with pytest.raises((DomainValidationError, ValidationError)):
            BankingReadinessPackage(
                bank_partner_id="mashreq_neobiz",
                kyc_kyb_checklist=["MOA"],
                business_plan_markdown="# Plan\nValid details here.",
                financial_projection_12m={},
                readiness_score=-5.0,  # Invalid: < 0.0
            )


class TestRegulatoryAlert:
    """Tests for RegulatoryAlert entity."""

    def test_valid_regulatory_alert(self) -> None:
        alert = RegulatoryAlert(
            alert_id="ALERT-2026-001",
            authority="DET",
            change_summary="Updated mainland trading documentation rules for IT services.",
            effective_date="2026-06-01",
            source_url="https://ded.dubai.gov.ae/updates/2026-001",
            impacted_workspace_ids=["ws-123", "ws-456"],
        )
        assert alert.alert_id == "ALERT-2026-001"
        assert len(alert.impacted_workspace_ids) == 2

    def test_empty_source_url_raises_error(self) -> None:
        with pytest.raises(DomainValidationError, match="source_url must not be empty"):
            RegulatoryAlert(
                alert_id="ALERT-2026-002",
                authority="IFZA",
                change_summary="New tariff structure for flexi-desk licenses.",
                effective_date="2026-07-01",
                source_url="   ",
            )


class TestDomainExceptions:
    """Tests confirming all domain exceptions inherit from DomainError."""

    @pytest.mark.parametrize(
        "exc_class",
        [
            DomainValidationError,
            JurisdictionConflictError,
            HITLApprovalRequiredError,
            ExternalIntegrationError,
        ],
    )
    def test_exceptions_inherit_from_domain_error(self, exc_class: type[Exception]) -> None:
        err = exc_class("Test error message")
        assert isinstance(err, DomainError)
        assert err.message == "Test error message"
        assert str(err) == "Test error message"


class TestPortContracts:
    """Tests verifying port abstract interfaces cannot be instantiated directly."""

    @pytest.mark.parametrize(
        "port_class",
        [
            WorkspaceRepositoryPort,
            RegulatorySearchPort,
            BankingWorkflowPort,
            ObservabilityPort,
            AgentOrchestratorPort,
        ],
    )
    def test_ports_cannot_be_instantiated_directly(self, port_class: type) -> None:
        with pytest.raises(TypeError):
            port_class()  # type: ignore[abstract]
