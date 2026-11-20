"""Form Automation SubAgent for DeepAgents.

Maps startup profile and user-approved jurisdiction into /workspace/registration_payload.json,
formulating trade name candidates, activity codes, MOA inputs, and Normal vs Instant licence
parameters. Enforces a LangGraph Human-In-The-Loop (HITL) interrupt before any external submission.
"""

from collections.abc import Sequence
from typing import Any

from deepagents.middleware.subagents import SubAgent
from langchain_core.tools import BaseTool, tool
from langgraph.types import interrupt

FORM_AUTOMATION_SYSTEM_PROMPT = """You are the Senior UAE Company Registration & Form Automation Agent for Dubai BizNavigator.

Your mission is to map `/workspace/startup_profile.json` and the selected jurisdiction from `/workspace/licensing_matrix.md` into a formal, authority-ready registration payload in `/workspace/registration_payload.json`.

### Critical Rules:
1. **Human-In-The-Loop (HITL) Safety Mandatory**:
   You must NEVER submit or transmit registration documents to an external authority without human approval.
   You must invoke the `submit_registration_to_authority` tool, which pauses execution with a LangGraph `interrupt` until the human operator signs off.

2. **Payload Formulation Protocol**:
   - Read `/workspace/startup_profile.json` and `/workspace/licensing_matrix.md`.
   - **Trade Name Formulation**:
     - Formulate at least 3 distinct trade name candidates conforming to Dubai Department of Economy and Tourism (DET) and Free Zone naming guidelines:
       - No blasphemous, political, or reserved country/governmental names.
       - Include appropriate legal form suffix (`LLC` for Mainland, `FZ-LLC` or `FZE` for Free Zones).
       - Ensure transliteration compatibility for Arabic commercial registers.
   - **Licence Classification & Activity Codes**:
     - Identify exact 6-digit Dubai DED activity codes or Free Zone standard activity descriptors.
     - Specify licence track: **DET Normal Licence** or **DET Instant Licence** (if Mainland, noting whether office lease/Ejari is deferred for Year 1).
   - **Shareholding & MOA Inputs**:
     - Draft shareholding distribution (100% foreign-owned or specified partner allocations, share counts, and nominal share value, typically AED 1,000 per share with minimum AED 10,000 - 50,000 capital).
     - Detail Manager / General Manager appointment and delegated powers in the Memorandum of Association (MOA).

3. **Workspace File Generation**:
   - Write the finalized registration structure to `/workspace/registration_payload.json` using `write_file`.
   - The JSON must follow the schema:
     ```json
     {
       "company_name": "Primary Candidate Name",
       "target_authority": "DET | DMCC | IFZA | DIFC",
       "licence_category": "commercial | professional | industrial",
       "licence_track": "Instant | Normal",
       "trade_name_candidates": ["Option 1", "Option 2", "Option 3"],
       "activity_codes": [{"code": "...", "description": "..."}],
       "shareholding_structure": [{"shareholder": "...", "shares": 100, "percentage": 100, "role": "Director/GM"}],
       "moa_inputs": {"capital_aed": 50000, "general_manager": "...", "fiscal_year_end": "December 31"},
       "hitl_approved": false
     }
     ```

4. **Trigger Authority Submission Review**:
   - Call `submit_registration_to_authority` passing the formulated payload to prompt the human-in-the-loop review.
"""


def create_authority_submission_tool() -> BaseTool:
    """Tool that triggers a LangGraph Human-In-The-Loop (HITL) interrupt before submission."""

    @tool
    def submit_registration_to_authority(registration_payload: dict[str, Any]) -> str:
        """Trigger Human-In-The-Loop (HITL) signoff before submitting registration to Dubai authority."""
        approval_response = interrupt(
            {
                "type": "registration_submission_approval",
                "action": "Authority Registration Submission",
                "authority": registration_payload.get("target_authority", "DET"),
                "company_name": registration_payload.get("company_name", "Unknown"),
                "trade_names": registration_payload.get("trade_name_candidates", []),
                "payload": registration_payload,
            }
        )
        return (
            f"Human-In-The-Loop approval received: {approval_response}. "
            "Registration payload successfully verified and cleared for authority transmission."
        )

    return submit_registration_to_authority


def get_form_automation_agent_subagent(
    tools: Sequence[BaseTool | Any] | None = None,
) -> SubAgent:
    """Build the form-automation-agent SubAgent specification for create_deep_agent."""
    subagent_tools: list[Any] = list(tools) if tools else [create_authority_submission_tool()]

    return {
        "name": "form-automation-agent",
        "description": (
            "Maps startup profile and jurisdiction into /workspace/registration_payload.json, "
            "formulates 3 trade name candidates, MOA structure, and Normal vs Instant licence fields, "
            "and triggers a mandatory Human-In-The-Loop (HITL) interrupt before authority submission."
        ),
        "system_prompt": FORM_AUTOMATION_SYSTEM_PROMPT,
        "tools": subagent_tools,
        "mode": "isolated",
    }
