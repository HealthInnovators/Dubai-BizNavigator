"""Unit tests validating A2UI Catalog, Surface Builder, and SSE Streamer against a2ui-core."""

import pytest
from a2ui.core.exceptions import A2uiValidationError
from a2ui.core.schema import CreateSurfaceMessage, UpdateComponentsMessage

from app.domain.entities import (
    AgentProgressEvent,
    BankingReadinessPackage,
    LicensingRecommendation,
    RegistrationPayload,
    StartupProfile,
)
from app.interfaces.a2ui.catalog import (
    BIZNAVIGATOR_CATALOG_ID,
    get_biznavigator_catalog,
    get_biznavigator_validator,
    validate_a2ui_component,
    validate_a2ui_components,
)
from app.interfaces.a2ui.sse_streamer import (
    A2UISSEStreamer,
    create_sse_response,
    format_sse_chunk,
    multiplex_agent_and_a2ui_stream,
)
from app.interfaces.a2ui.surface_builder import A2UISurfaceBuilder


class TestA2UICatalog:
    """Tests for the BizNavigator A2UI widget catalog and schema validation."""

    def test_catalog_contains_all_11_required_widgets(self):
        catalog = get_biznavigator_catalog()
        assert catalog.catalog_id == BIZNAVIGATOR_CATALOG_ID

        expected_widgets = [
            "Text",
            "Column",
            "Row",
            "Card",
            "DataTable",
            "Badge",
            "TextField",
            "Select",
            "Button",
            "ApprovalGateCard",
            "MarkdownViewer",
        ]
        registered_components = set(catalog.components.keys())
        for widget in expected_widgets:
            assert widget in registered_components, f"Widget '{widget}' not in catalog"

    def test_component_validation_success(self):
        valid_card = {
            "id": "c1",
            "component": "Card",
            "title": "Test Card",
            "child": "t1",
            "variant": "elevated",
        }
        valid_text = {
            "id": "t1",
            "component": "Text",
            "text": "Hello Dubai",
            "variant": "heading",
        }
        valid_button = {
            "id": "b1",
            "component": "Button",
            "label": "Click me",
            "action": {"event": "test_action"},
            "variant": "primary",
        }

        # Should not raise
        validate_a2ui_component(valid_card)
        validate_a2ui_components([valid_card, valid_text, valid_button])

    def test_component_validation_rejection_for_unknown_component(self):
        invalid_comp = {
            "id": "unk1",
            "component": "NonExistentWidget",
            "data": "bad",
        }
        with pytest.raises(A2uiValidationError):
            validate_a2ui_component(invalid_comp)

    def test_validator_instance_reusability(self):
        v1 = get_biznavigator_validator()
        v2 = get_biznavigator_validator()
        assert v1 is v2


class TestA2UISurfaceBuilder:
    """Tests for A2UISurfaceBuilder producing valid wire-stable surfaces."""

    @pytest.fixture
    def builder(self) -> A2UISurfaceBuilder:
        return A2UISurfaceBuilder()

    @pytest.fixture
    def sample_profile(self) -> StartupProfile:
        return StartupProfile(
            company_name="Apex AI Technologies LLC",
            industry_sector="Artificial Intelligence",
            business_activity="Software Development & AI Consultancy",
            revenue_model="B2B_SaaS",
            uae_local_trade=True,
            visa_quota_needed=5,
            office_preference="PhysicalOffice",
            founders_summary="2 Founders (German, British)",
        )

    def test_build_intake_form_surface(self, builder, sample_profile):
        messages = builder.build_intake_form_surface(
            surface_id="test_intake",
            default_profile=sample_profile,
        )

        assert len(messages) == 2
        assert isinstance(messages[0], CreateSurfaceMessage)
        assert isinstance(messages[1], UpdateComponentsMessage)

        assert messages[0].create_surface.surface_id == "test_intake"
        assert messages[0].create_surface.catalog_id == BIZNAVIGATOR_CATALOG_ID

        components = messages[1].update_components.components
        comp_map = {c["id"]: c for c in components}

        assert "intake_root" in comp_map
        assert "field_company_name" in comp_map
        assert comp_map["field_company_name"]["value"] == "Apex AI Technologies LLC"
        assert comp_map["field_uae_local_trade"]["value"] == "true"
        assert comp_map["btn_submit_intake"]["component"] == "Button"

        wire_dicts = builder.to_wire_dicts(messages)
        assert wire_dicts[0]["createSurface"]["surfaceId"] == "test_intake"
        assert "updateComponents" in wire_dicts[1]

    def test_build_licensing_matrix_surface(self, builder):
        recommendations = [
            LicensingRecommendation(
                pathway="Mainland_DET",
                recommended_authority="DET Dubai Economy & Tourism",
                licence_type="Commercial Licence",
                estimated_cost_aed_min=18500,
                estimated_cost_aed_max=24000,
                visa_capacity=5,
                mainland_trading_notes="100% foreign ownership allowed under Commercial Companies Law.",
                source_urls=["https://dubaidet.gov.ae/en/services/instant-licence"],
            ),
            LicensingRecommendation(
                pathway="FreeZone",
                recommended_authority="DMCC Dubai Multi Commodities Centre",
                licence_type="Service Licence",
                estimated_cost_aed_min=20000,
                estimated_cost_aed_max=35000,
                visa_capacity=3,
                mainland_trading_notes="Requires mainland commercial distributor for physical onshore sales.",
                source_urls=["https://dmcc.ae/free-zone/setup-process"],
            ),
        ]

        messages = builder.build_licensing_matrix_surface(
            recommendations=recommendations,
            surface_id="test_matrix",
        )

        assert len(messages) == 2
        update_msg = messages[1]
        comp_map = {c["id"]: c for c in update_msg.update_components.components}

        assert "licensing_datatable" in comp_map
        dt = comp_map["licensing_datatable"]
        assert dt["component"] == "DataTable"
        assert len(dt["rows"]) == 2
        assert dt["rows"][0]["pathway"] == "Mainland_DET"
        assert dt["rows"][1]["pathway"] == "FreeZone"

        assert "card_rec_0" in comp_map
        assert "badge_rec_0" in comp_map
        assert comp_map["badge_rec_0"]["text"] == "Mainland_DET"
        assert comp_map["badge_rec_0"]["variant"] == "success"

        assert "card_rec_1" in comp_map
        assert "badge_rec_1" in comp_map
        assert comp_map["badge_rec_1"]["text"] == "FreeZone"
        assert comp_map["badge_rec_1"]["variant"] == "info"

    def test_build_hitl_approval_surface_registration(self, builder):
        payload = RegistrationPayload(
            target_authority="DET",
            licence_category="Commercial",
            trade_name_candidates=["Apex AI LLC", "Apex Tech LLC"],
            shareholding_structure=[{"shareholder": "Jane Doe", "percentage": 100.0}],
        )

        messages = builder.build_hitl_approval_surface(
            payload_or_package=payload,
            action_type="registration",
            surface_id="test_hitl_reg",
        )

        assert len(messages) == 2
        components = messages[1].update_components.components
        comp_map = {c["id"]: c for c in components}

        assert "gate_card" in comp_map
        gate = comp_map["gate_card"]
        assert gate["component"] == "ApprovalGateCard"
        assert gate["status"] == "pending"
        assert gate["payload_preview"]["target_authority"] == "DET"

        assert comp_map["btn_approve"]["action"]["event"] == "hitl_approve"
        assert comp_map["btn_reject"]["action"]["event"] == "hitl_reject"

    def test_build_hitl_approval_surface_banking(self, builder):
        package = BankingReadinessPackage(
            bank_partner_id="Wio_Business_API",
            kyc_kyb_checklist=["Trade Licence", "Ejari", "Passport Copy"],
            business_plan_markdown="# Executive Business Plan and Strategy",
            financial_projection_12m={"revenue_m12": 500000},
            readiness_score=92,
        )

        messages = builder.build_hitl_approval_surface(
            payload_or_package=package,
            action_type="banking",
            surface_id="test_hitl_bank",
        )

        components = messages[1].update_components.components
        comp_map = {c["id"]: c for c in components}

        gate = comp_map["gate_card"]
        assert gate["payload_preview"]["bank_partner_id"] == "Wio_Business_API"
        assert gate["payload_preview"]["readiness_score"] == 92

    def test_build_business_plan_surface(self, builder):
        bp_md = "# Executive Business Plan\n## Growth Strategy"
        comp_md = "# KYB Checklist\n- [x] Board Resolution"
        urls = {
            "business_plan": "/workspace/business_plan.md",
            "compliance_checklist": "/workspace/compliance_checklist.md",
        }

        messages = builder.build_business_plan_surface(
            business_plan_md=bp_md,
            compliance_md=comp_md,
            artifact_urls=urls,
            surface_id="test_bp_surface",
        )

        assert len(messages) == 2
        comp_map = {c["id"]: c for c in messages[1].update_components.components}

        assert "viewer_business_plan" in comp_map
        bp_viewer = comp_map["viewer_business_plan"]
        assert bp_viewer["component"] == "MarkdownViewer"
        assert bp_viewer["content"] == bp_md
        assert bp_viewer["download_links"][0]["url"] == "/workspace/business_plan.md"

        assert "viewer_compliance" in comp_map
        comp_viewer = comp_map["viewer_compliance"]
        assert comp_viewer["content"] == comp_md


class TestSSEStreamer:
    """Tests for SSE multiplexing and streaming response generation."""

    def test_format_sse_chunk(self):
        chunk = format_sse_chunk(
            event="agent_progress",
            data={"agent_name": "licensing-strategist", "status": "running"},
            event_id="evt_1",
        )
        assert "id: evt_1\n" in chunk
        assert "event: agent_progress\n" in chunk
        assert '"agent_name": "licensing-strategist"' in chunk
        assert chunk.endswith("\n\n")

    @pytest.mark.asyncio
    async def test_multiplex_stream_progress_and_hitl(self):
        async def fake_orchestrator_stream():
            yield AgentProgressEvent(
                agent_name="licensing-strategist",
                status="running",
                message="Analyzing jurisdiction parameters...",
            )
            yield AgentProgressEvent(
                agent_name="form-automation-agent",
                status="interrupted",
                hitl_interrupt=True,
                message="User approval required for DET registration payload.",
                payload={"target_authority": "DET", "licence_category": "Commercial"},
            )

        collected_events: list[str] = []
        async for chunk in multiplex_agent_and_a2ui_stream(fake_orchestrator_stream()):
            collected_events.append(chunk)

        full_stream_text = "".join(collected_events)

        # Check agent_progress emitted
        assert "event: agent_progress" in full_stream_text
        assert "Analyzing jurisdiction parameters..." in full_stream_text

        # Check A2UI surface emitted on HITL interrupt
        assert "event: a2ui_surface" in full_stream_text
        assert "createSurface" in full_stream_text
        assert "updateComponents" in full_stream_text

        # Check hitl_interrupt emitted
        assert "event: hitl_interrupt" in full_stream_text

        # Check stream_complete emitted at the end
        assert "event: stream_complete" in full_stream_text

    @pytest.mark.asyncio
    async def test_multiplex_stream_artifact_update(self):
        async def fake_orchestrator_stream():
            yield AgentProgressEvent(
                agent_name="banking-readiness-agent",
                status="running",
                artifact_updated="/workspace/business_plan.md",
                message="Executive summary and financial model finalized.",
            )

        collected_events: list[str] = []
        async for chunk in multiplex_agent_and_a2ui_stream(fake_orchestrator_stream()):
            collected_events.append(chunk)

        full_stream_text = "".join(collected_events)

        assert "event: agent_progress" in full_stream_text
        assert "event: a2ui_surface" in full_stream_text
        assert "viewer_business_plan" in full_stream_text

    def test_create_sse_response_metadata(self):
        async def dummy_gen():
            yield "data: hello\n\n"

        response = create_sse_response(dummy_gen())
        assert response.media_type == "text/event-stream"
        assert response.headers["Cache-Control"] == "no-cache"
        assert response.headers["Connection"] == "keep-alive"

    def test_a2ui_sse_streamer_facade(self):
        class MockOrchestrator:
            async def stream_subagents(self, profile, session_id, tenant_id):
                yield AgentProgressEvent(
                    agent_name="licensing-strategist",
                    status="running",
                )

            async def resume_execution(self, resume_action, session_id, tenant_id):
                yield AgentProgressEvent(
                    agent_name="form-automation-agent",
                    status="completed",
                )

        streamer = A2UISSEStreamer(orchestrator=MockOrchestrator())

        profile = StartupProfile(
            company_name="Test Corp",
            industry_sector="Tech",
            business_activity="Consulting",
            revenue_model="B2B",
            uae_local_trade=False,
            visa_quota_needed=2,
            office_preference="FlexiDesk",
            founders_summary="Solo Founder",
        )

        resp1 = streamer.stream_workflow(profile, "sess_1", "tenant_1")
        assert resp1.media_type == "text/event-stream"

        resp2 = streamer.stream_resumption("hitl_approve", "sess_1", "tenant_1")
        assert resp2.media_type == "text/event-stream"
