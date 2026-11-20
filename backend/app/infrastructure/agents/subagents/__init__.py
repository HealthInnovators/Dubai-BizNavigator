"""Specialized DeepAgents subagents package for Dubai BizNavigator."""

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
from app.infrastructure.agents.subagents.licensing_strategist import (
    LICENSING_STRATEGIST_SYSTEM_PROMPT,
    get_licensing_strategist_subagent,
)
from app.infrastructure.agents.subagents.regulatory_researcher import (
    REGULATORY_RESEARCHER_SYSTEM_PROMPT,
    get_regulatory_researcher_subagent,
)

__all__ = [
    # Prompts
    "BANKING_READINESS_SYSTEM_PROMPT",
    "COMPLIANCE_AUDITOR_SYSTEM_PROMPT",
    "FORM_AUTOMATION_SYSTEM_PROMPT",
    "LICENSING_STRATEGIST_SYSTEM_PROMPT",
    "REGULATORY_RESEARCHER_SYSTEM_PROMPT",
    # Subagents
    "get_banking_readiness_agent_subagent",
    "get_compliance_auditor_subagent",
    "get_form_automation_agent_subagent",
    "get_licensing_strategist_subagent",
    "get_regulatory_researcher_subagent",
    # Tools
    "create_authority_submission_tool",
    "create_banking_tools",
    "create_compliance_auditor_tools",
]
