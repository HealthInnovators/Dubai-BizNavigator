"""Unit tests for DeepAgents Orchestrator.

Verifies:
1. Langfuse callback injection in execution config.
2. Checkpointer thread_id scoping per workspace.
3. Virtual filesystem artifact pre-population.
4. Stream subagents event mapping into typed domain progress events.
5. HITL interrupt detection and resumption lifecycle.
"""

import json
from collections.abc import AsyncGenerator
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.domain.entities import RegistrationPayload, StartupProfile
from app.domain.exceptions import HITLApprovalRequiredError
from app.infrastructure.agents.orchestrator import (
    WORKSPACE_ARTIFACT_PATHS,
    AgentProgressEvent,
    DeepAgentsOrchestrator,
)


@pytest.fixture
def sample_profile() -> StartupProfile:
    return StartupProfile(
        company_name="Falcon Quantum AI",
        industry_sector="DeepTech",
        business_activity="Quantum software development and cloud AI",
        revenue_model="Enterprise License and Compute Credits",
        uae_local_trade=False,
        visa_quota_needed=4,
        office_preference="flexi_desk",
        founders_summary="AI researchers from Abu Dhabi & Dubai.",
    )


class TestConfigAndCallbackInjection:
    """Verify checkpointer thread_id scoping and Langfuse callback injection."""

    def test_callback_injected_when_langfuse_adapter_present(self) -> None:
        mock_adapter = MagicMock()
        mock_handler = MagicMock()
        mock_adapter.get_langchain_callback_handler.return_value = mock_handler

        orchestrator = DeepAgentsOrchestrator(
            langfuse_adapter=mock_adapter,
            agent_instance=MagicMock(),
        )

        config = orchestrator._build_config(workspace_id="ws-uae-456", tenant_id="tenant-99")
        assert config["configurable"]["thread_id"] == "ws-uae-456"
        assert config["metadata"]["workspace_id"] == "ws-uae-456"
        assert config["metadata"]["tenant_id"] == "tenant-99"
        assert mock_handler in config["callbacks"]
        mock_adapter.get_langchain_callback_handler.assert_called_once()

    def test_config_without_langfuse_adapter(self) -> None:
        orchestrator = DeepAgentsOrchestrator(
            langfuse_adapter=None,
            agent_instance=MagicMock(),
        )

        config = orchestrator._build_config(workspace_id="ws-simple-123")
        assert config["configurable"]["thread_id"] == "ws-simple-123"
        assert config["callbacks"] == []


class TestVirtualFilesystemArtifacts:
    """Verify the 5 required structured artifacts are configured in /workspace/."""

    def test_workspace_files_contain_all_required_artifacts(
        self, sample_profile: StartupProfile
    ) -> None:
        orchestrator = DeepAgentsOrchestrator(agent_instance=MagicMock())
        files = orchestrator._build_workspace_files(sample_profile)

        for path in WORKSPACE_ARTIFACT_PATHS:
            assert path in files, f"Missing required artifact path: {path}"

        # Verify JSON artifacts parse validly
        startup_data = json.loads(files["/workspace/startup_profile.json"])
        assert startup_data["company_name"] == "Falcon Quantum AI"

        registration_data = json.loads(files["/workspace/registration_payload.json"])
        assert registration_data["company_name"] == "Falcon Quantum AI"
        assert registration_data["hitl_approved"] is False


class TestSubagentsAssembly:
    """Verify the trio of specialized subagents are constructed."""

    def test_subagents_contain_all_specialists(self) -> None:
        orchestrator = DeepAgentsOrchestrator(agent_instance=MagicMock())
        subagents = orchestrator._build_subagents()
        names = [sa["name"] for sa in subagents]

        assert "licensing-strategist" in names
        assert "regulatory-researcher" in names
        assert "form-automation-agent" in names
        assert "banking-readiness-agent" in names
        assert "compliance-auditor" in names


class TestStreamEventMapping:
    """Verify raw stream chunks map to typed AgentProgressEvent instances."""

    @pytest.mark.asyncio
    @patch("app.infrastructure.agents.orchestrator.propagate_attributes")
    async def test_stream_subagents_lifecycle_and_tool_mapping(
        self,
        mock_propagate: MagicMock,
        sample_profile: StartupProfile,
    ) -> None:
        mock_propagate.return_value.__enter__.return_value = None

        # Build mock agent that yields synthetic LangGraph stream chunks
        mock_agent = MagicMock()

        async def fake_astream(*args: Any, **kwargs: Any) -> AsyncGenerator[tuple[Any, Any], None]:
            # Subagent tool execution
            from langchain_core.messages import AIMessage

            yield (
                ("tools:task", "licensing_specialist"),
                {
                    "messages": [
                        AIMessage(
                            content="Analyzing licensing requirements...",
                            tool_calls=[
                                {
                                    "id": "call_write_1",
                                    "name": "write_file",
                                    "args": {"path": "/workspace/licensing_matrix.md"},
                                }
                            ],
                        )
                    ],
                    "files": {
                        "/workspace/licensing_matrix.md": "# Updated Matrix",
                    },
                },
            )

        mock_agent.astream = fake_astream

        orchestrator = DeepAgentsOrchestrator(agent_instance=mock_agent)

        events: list[AgentProgressEvent] = []
        async for evt in orchestrator.stream_subagents(
            profile=sample_profile, workspace_id="ws-stream-1"
        ):
            events.append(evt)

        # Check initial start event
        assert events[0].agent_name == "coordinator"
        assert events[0].status == "started"

        # Check subagent tool call mapping
        tool_events = [e for e in events if e.tool_call is not None]
        assert len(tool_events) >= 1
        assert tool_events[0].agent_name == "licensing_specialist"
        assert tool_events[0].tool_call["name"] == "write_file"
        assert tool_events[0].artifact_updated == "/workspace/licensing_matrix.md"

        # Check completion event
        assert events[-1].agent_name == "coordinator"
        assert events[-1].status == "completed"

    def test_parse_chunk_detects_hitl_interrupt(self) -> None:
        orchestrator = DeepAgentsOrchestrator(agent_instance=MagicMock())
        interrupt_chunk = (
            (),
            {
                "__interrupt__": "Awaiting founder signature for DET submission.",
            },
        )
        parsed = orchestrator._parse_stream_chunk(interrupt_chunk)
        assert len(parsed) == 1
        assert parsed[0].status == "interrupted"
        assert parsed[0].hitl_interrupt is True
        assert "Human-In-The-Loop approval" in parsed[0].message


class TestHITLResumption:
    """Verify Human-In-The-Loop resumption mechanics."""

    @pytest.mark.asyncio
    @patch("app.infrastructure.agents.orchestrator.propagate_attributes")
    async def test_resume_hitl_workflow_success(
        self, mock_propagate: MagicMock
    ) -> None:
        mock_propagate.return_value.__enter__.return_value = None

        mock_agent = MagicMock()
        mock_agent.ainvoke = AsyncMock(return_value={"status": "dispatched_to_det"})

        orchestrator = DeepAgentsOrchestrator(agent_instance=mock_agent)

        payload = RegistrationPayload(
            target_authority="DET",
            licence_category="Commercial",
            trade_name_candidates=["Falcon Innovations LLC"],
        )
        payload.approve_hitl()

        result = await orchestrator.resume_hitl_workflow(
            workspace_id="ws-hitl-999", registration_payload=payload
        )

        assert result["workspace_id"] == "ws-hitl-999"
        assert result["status"] == "resumed"
        mock_agent.ainvoke.assert_called_once()
        command_arg = mock_agent.ainvoke.call_args.args[0]
        assert command_arg.resume["approved"] is True

    @pytest.mark.asyncio
    async def test_resume_unapproved_payload_raises_error(self) -> None:
        orchestrator = DeepAgentsOrchestrator(agent_instance=MagicMock())
        unapproved_payload = RegistrationPayload(
            target_authority="IFZA",
            licence_category="Commercial",
            trade_name_candidates=["Unapproved Tech FZ-LLC"],
        )
        with pytest.raises(HITLApprovalRequiredError):
            await orchestrator.resume_hitl_workflow(
                workspace_id="ws-err-1", registration_payload=unapproved_payload
            )
