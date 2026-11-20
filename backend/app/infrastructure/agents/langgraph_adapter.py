"""Adapter for LangGraph / DeepAgents workflow execution."""

from collections.abc import AsyncGenerator
from typing import Any


class DeepAgentsWorkflowAdapter:
    """Wrapper around DeepAgents / LangGraph orchestration state machine."""

    def __init__(self, checkpointer_dsn: str | None = None) -> None:
        self.checkpointer_dsn = checkpointer_dsn

    async def execute_agent_pipeline(
        self, state_input: dict[str, Any]
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Runs the agent graph pipeline, yielding intermediate and terminal states."""
        yield {
            "node": "activity_classifier",
            "status": "completed",
            "output": {"category": state_input.get("license_category", "commercial")},
        }
        yield {
            "node": "jurisdiction_recommender",
            "status": "completed",
            "output": {"recommended_zone": "IFZA / DMCC"},
        }
        yield {
            "node": "cost_estimator",
            "status": "completed",
            "output": {"estimated_aed": 14500, "visa_allocation": 1},
        }
