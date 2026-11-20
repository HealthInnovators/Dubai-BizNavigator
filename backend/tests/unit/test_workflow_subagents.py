"""Unit tests for remaining DeepAgents subagents:

1. form-automation-agent (trade names, MOA inputs, Normal vs Instant, HITL interrupt).
2. banking-readiness-agent (KYC retrieval, business plan, 12m projection, source of funds, HITL interrupt).
3. compliance-auditor (read-only critique, citation verification, schema completeness, zero leaked PII).
4. DeepAgentsOrchestrator registration of all 5 subagents.
"""

from unittest.mock import MagicMock, patch

from app.infrastructure.agents.orchestrator import DeepAgentsOrchestrator
from app.infrastructure.agents.subagents.banking_readiness_agent import (
    BANKING_READINESS_SYSTEM_PROMPT,
    create_banking_tools,
    get_banking_readiness_agent_subagent,
)
from app.infrastructure.agents.subagents.compliance_auditor import (
    COMPLIANCE_AUDITOR_SYSTEM_PROMPT,
    create_compliance_auditor_tools,
    get_compliance_auditor_subagent,
)
from app.infrastructure.agents.subagents.form_automation_agent import (
    FORM_AUTOMATION_SYSTEM_PROMPT,
    create_authority_submission_tool,
    get_form_automation_agent_subagent,
)


class TestFormAutomationAgent:
    """Tests for form-automation-agent subagent specification and HITL interrupt tool."""

    def test_spec_name_and_tools(self) -> None:
        subagent = get_form_automation_agent_subagent()
        assert subagent["name"] == "form-automation-agent"
        assert len(subagent["tools"]) >= 1
        tool_names = [t.name for t in subagent["tools"]]
        assert "submit_registration_to_authority" in tool_names

    def test_prompt_covers_trade_names_moa_and_instant_licence(self) -> None:
        prompt = FORM_AUTOMATION_SYSTEM_PROMPT
        assert "/workspace/registration_payload.json" in prompt
        assert "trade name candidates" in prompt.lower()
        assert "DET Normal Licence" in prompt
        assert "DET Instant Licence" in prompt
        assert "Memorandum of Association" in prompt
        assert "Human-In-The-Loop" in prompt

    @patch("app.infrastructure.agents.subagents.form_automation_agent.interrupt")
    def test_submit_registration_tool_triggers_hitl_interrupt(
        self, mock_interrupt: MagicMock
    ) -> None:
        mock_interrupt.return_value = {"approved": True, "reviewer": "officer_1"}
        tool_instance = create_authority_submission_tool()

        test_payload = {
            "company_name": "Falcon Quantum AI LLC",
            "target_authority": "DET",
            "trade_name_candidates": ["Falcon Quantum AI LLC", "Falcon AI Tech LLC"],
            "licence_category": "commercial",
            "licence_track": "Instant",
        }

        result = tool_instance.invoke({"registration_payload": test_payload})

        mock_interrupt.assert_called_once()
        interrupt_arg = mock_interrupt.call_args[0][0]
        assert interrupt_arg["type"] == "registration_submission_approval"
        assert interrupt_arg["authority"] == "DET"
        assert interrupt_arg["company_name"] == "Falcon Quantum AI LLC"
        assert "Falcon Quantum AI LLC" in interrupt_arg["trade_names"]
        assert "Human-In-The-Loop approval received" in result


class TestBankingReadinessAgent:
    """Tests for banking-readiness-agent subagent specification and banking tools."""

    def test_spec_name_and_tools(self) -> None:
        subagent = get_banking_readiness_agent_subagent()
        assert subagent["name"] == "banking-readiness-agent"
        assert len(subagent["tools"]) >= 2
        tool_names = [t.name for t in subagent["tools"]]
        assert "get_banking_kyc_requirements" in tool_names
        assert "submit_to_banking_partner" in tool_names

    def test_prompt_covers_business_plan_and_compliance_checklist(self) -> None:
        prompt = BANKING_READINESS_SYSTEM_PROMPT
        assert "/workspace/business_plan.md" in prompt
        assert "/workspace/compliance_checklist.md" in prompt
        assert "UAE Market Entry & Operational Strategy" in prompt
        assert "Source of Funds & Capital Inflow Narrative" in prompt
        assert "12-Month Financial Projections" in prompt
        assert "Wio Business Bank" in prompt or "Wio" in prompt

    def test_get_banking_kyc_requirements_tool(self) -> None:
        tools = create_banking_tools()
        kyc_tool = next(t for t in tools if t.name == "get_banking_kyc_requirements")

        result = kyc_tool.invoke({"bank_partner_id": "wio_business", "licence_category": "commercial"})
        assert "Trade Licence" in result
        assert "Shareholder & UBO passports" in result
        assert "Source-of-funds declaration" in result

    @patch("app.infrastructure.agents.subagents.banking_readiness_agent.interrupt")
    def test_submit_to_banking_partner_triggers_hitl_interrupt(
        self, mock_interrupt: MagicMock
    ) -> None:
        mock_interrupt.return_value = {"approved": True, "comments": "Cleared for Wio onboarding"}
        tools = create_banking_tools()
        submit_tool = next(t for t in tools if t.name == "submit_to_banking_partner")

        package = {
            "company_name": "Falcon Quantum AI LLC",
            "readiness_score": 92.5,
            "business_plan_path": "/workspace/business_plan.md",
        }

        result = submit_tool.invoke({"bank_partner_id": "wio_business", "readiness_package": package})

        mock_interrupt.assert_called_once()
        interrupt_arg = mock_interrupt.call_args[0][0]
        assert interrupt_arg["type"] == "banking_submission_approval"
        assert interrupt_arg["bank_partner_id"] == "wio_business"
        assert interrupt_arg["readiness_score"] == 92.5
        assert "Human-In-The-Loop approval received" in result


class TestComplianceAuditorAgent:
    """Tests for compliance-auditor read-only critique subagent."""

    def test_spec_name_and_readonly_permissions(self) -> None:
        subagent = get_compliance_auditor_subagent()
        assert subagent["name"] == "compliance-auditor"
        assert "read-only critique" in subagent["description"].lower()

        # Verify filesystem permissions deny write operations
        permissions = subagent.get("permissions", [])
        assert len(permissions) >= 1
        perm = permissions[0]
        mode = perm.mode if hasattr(perm, "mode") else perm["mode"]
        ops = perm.operations if hasattr(perm, "operations") else perm["operations"]
        assert mode == "deny"
        assert "write" in ops

    def test_prompt_covers_critique_dimensions(self) -> None:
        prompt = COMPLIANCE_AUDITOR_SYSTEM_PROMPT
        assert "READ-ONLY" in prompt
        assert "Citation & Source URL Verification" in prompt
        assert "Schema Completeness & Consistency" in prompt
        assert "Zero Leaked PII Audit" in prompt
        assert "Ungrounded Claims Detection" in prompt
        assert "/workspace/licensing_matrix.md" in prompt
        assert "/workspace/business_plan.md" in prompt
        assert "/workspace/compliance_checklist.md" in prompt

    def test_record_audit_verdict_tool(self) -> None:
        tools = create_compliance_auditor_tools()
        verdict_tool = tools[0]

        passed_res = verdict_tool.invoke(
            {
                "verdict": "APPROVED",
                "quality_score": 95,
                "citation_integrity": True,
                "schema_completeness": True,
                "pii_clean": True,
                "critique_notes": "All legal claims cited, no PII leakage.",
            }
        )
        assert "PASSED" in passed_res
        assert "95/100" in passed_res

        failed_res = verdict_tool.invoke(
            {
                "verdict": "CHANGES_REQUIRED",
                "quality_score": 60,
                "citation_integrity": True,
                "schema_completeness": True,
                "pii_clean": False,  # Leaked PII detected!
                "critique_notes": "Unredacted Emirates ID found in business plan.",
            }
        )
        assert "REMEDIATION_REQUIRED" in failed_res


class TestOrchestratorSubagentsRegistration:
    """Verify all 5 subagents are registered in DeepAgentsOrchestrator."""

    def test_orchestrator_has_all_five_subagents(self) -> None:
        orchestrator = DeepAgentsOrchestrator(agent_instance=MagicMock())
        subagents = orchestrator._build_subagents()
        subagent_names = [sa["name"] for sa in subagents]

        expected_subagents = [
            "licensing-strategist",
            "regulatory-researcher",
            "form-automation-agent",
            "banking-readiness-agent",
            "compliance-auditor",
        ]

        assert len(subagents) == 5
        for name in expected_subagents:
            assert name in subagent_names, f"Subagent {name} not registered in orchestrator"
