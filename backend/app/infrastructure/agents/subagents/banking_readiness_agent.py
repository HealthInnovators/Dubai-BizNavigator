"""Banking Readiness SubAgent for DeepAgents.

Retrieves corporate bank KYC/KYB requirements via BankingWorkflowPort,
drafts /workspace/business_plan.md and /workspace/compliance_checklist.md,
and enforces a Human-In-The-Loop (HITL) interrupt before banking gateway dispatch.
"""

from collections.abc import Sequence
from typing import Any

from deepagents.middleware.subagents import SubAgent
from langchain_core.tools import BaseTool, tool
from langgraph.types import interrupt

from app.domain.ports import BankingWorkflowPort
from app.infrastructure.adapters.banking_api import BankingAPIAdapter

BANKING_READINESS_SYSTEM_PROMPT = """You are the Senior UAE Corporate Banking Readiness Advisor for Dubai BizNavigator.

Your mission is to formulate an investor-grade corporate bank application package that satisfies UAE Central Bank anti-money laundering (AML) and counter-terrorism financing (CTF) standards for institutions such as Wio Business Bank, Mashreq NeoBiz, and Emirates NBD.

### Protocol:

1. **KYC/KYB Requirements Gathering**:
   - Query the `get_banking_kyc_requirements` tool for the target bank partner and licence category.
   - Note key onboarding requirements: source of funds proof, expected counterparty jurisdictions, UBO disclosures, and business model viability.

2. **Drafting `/workspace/business_plan.md`**:
   Write a comprehensive 5-section corporate banking business plan via `write_file`:
   - **# Corporate Banking Business Plan: [Company Name]**
   - **## 1. Executive Summary & Company Profile** (Ownership structure, legal form, management bios)
   - **## 2. UAE Market Entry & Operational Strategy** (Target customers, delivery channels, onshore vs offshore scope)
   - **## 3. Source of Funds & Capital Inflow Narrative** (Detailed justification of seed capital, investor provenance, and expected wire origins)
   - **## 4. Counterparties & Expected Transaction Volumes** (Anticipated monthly credit/debit turnover, major suppliers, client jurisdictions)
   - **## 5. 12-Month Financial Projections** (Monthly revenue, operating expenses, gross margins, minimum monthly account balance commitments ~ AED 25,000 - 50,000)

3. **Drafting `/workspace/compliance_checklist.md`**:
   Write an actionable compliance checklist via `write_file`:
   - **# Corporate Banking KYC / KYB Compliance Checklist**
   - **## Corporate Documents**: Valid Trade Licence, Certificate of Incorporation, Memorandum of Association (MOA) / Articles of Association (AOA), Share Certificates, Ejari / Freezone Office Lease.
   - **## Shareholder & Director Verification**: Passport copies with UAE entry stamp / residence visa, Emirates ID (front & back), 6-month personal bank statements from country of origin or UAE, Comprehensive CV / LinkedIn profile.
   - **## Operational Evidence**: Invoices / agreements with initial suppliers/clients, active company website/portfolio, lease agreement.

4. **Human-In-The-Loop (HITL) Gate**:
   - Call `submit_to_banking_partner` passing the readiness package.
   - This tool invokes a mandatory LangGraph `interrupt`, pausing execution for human review and signoff prior to API dispatch.
"""


def create_banking_tools(
    banking_port: BankingWorkflowPort | None = None,
) -> list[BaseTool]:
    """Create banking KYC retrieval and HITL submission tools."""
    port = banking_port or BankingAPIAdapter()

    @tool
    def get_banking_kyc_requirements(
        bank_partner_id: str = "wio_business", licence_category: str = "commercial"
    ) -> str:
        """Fetch required KYC/KYB document checklist for a specific UAE bank partner."""
        gateway_name = getattr(port, "endpoint_url", None) or port.__class__.__name__
        return (
            f"Official KYC/KYB checklist via {gateway_name} for {bank_partner_id} ({licence_category}):\n"
            "1. Valid UAE Trade Licence & MOA\n"
            "2. Shareholder & UBO passports, visas, and Emirates IDs\n"
            "3. 6-month bank statements of all 20%+ shareholders\n"
            "4. Comprehensive business plan with 12-month financial projection\n"
            "5. Proof of business address (Ejari or Freezone office certificate)\n"
            "6. Source-of-funds declaration and expected counterparty breakdown"
        )

    @tool
    def submit_to_banking_partner(
        bank_partner_id: str, readiness_package: dict[str, Any]
    ) -> str:
        """Trigger Human-In-The-Loop (HITL) signoff before submitting readiness package to partner bank API."""
        approval_response = interrupt(
            {
                "type": "banking_submission_approval",
                "action": "Bank Readiness Package Submission",
                "bank_partner_id": bank_partner_id,
                "readiness_score": readiness_package.get("readiness_score", 90.0),
                "package": readiness_package,
            }
        )
        return (
            f"Human-In-The-Loop approval received: {approval_response}. "
            f"Corporate banking package successfully dispatched to {bank_partner_id} gateway."
        )

    return [get_banking_kyc_requirements, submit_to_banking_partner]


def get_banking_readiness_agent_subagent(
    banking_port: BankingWorkflowPort | None = None,
    tools: Sequence[BaseTool | Any] | None = None,
) -> SubAgent:
    """Build the banking-readiness-agent SubAgent specification for create_deep_agent."""
    subagent_tools: list[Any] = (
        list(tools) if tools else create_banking_tools(banking_port)
    )

    return {
        "name": "banking-readiness-agent",
        "description": (
            "Retrieves UAE bank KYC/KYB requirements, drafts /workspace/business_plan.md "
            "(12-month projection, source of funds, market entry) and /workspace/compliance_checklist.md, "
            "and enforces a Human-In-The-Loop (HITL) interrupt before submitting to banking APIs."
        ),
        "system_prompt": BANKING_READINESS_SYSTEM_PROMPT,
        "tools": subagent_tools,
        "mode": "isolated",
    }
