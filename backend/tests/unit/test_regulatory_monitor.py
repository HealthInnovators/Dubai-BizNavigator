"""Unit tests for the Regulatory Update Monitor, background worker, and A2UI alert surface."""

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from app.application.regulatory_monitor import (
    DEFAULT_REGULATORY_TOPICS,
    RegulatoryUpdateMonitor,
)
from app.domain.entities import RegulatoryAlert, StartupProfile
from app.domain.ports import RegulatorySearchPort
from app.infrastructure.database.postgres_adapter import (
    PostgresBusinessProfileRepository,
)
from app.infrastructure.workers.monitor_worker import RegulatoryMonitorWorker
from app.interfaces.a2ui.surface_builder import A2UISurfaceBuilder
from app.interfaces.container import Container, get_container
from app.main import app


class MockRegulatorySearch(RegulatorySearchPort):
    """Mock search port returning controlled regulatory snippets."""

    def __init__(self, snippets: list[dict[str, Any]] | None = None) -> None:
        self.snippets = snippets or [
            {
                "title": "Dubai DET Instant Licence Eligibility Expansion",
                "snippet": "Dubai DET expands Instant Licence categories to include 100% foreign-owned AI consulting.",
                "url": "https://dubaidet.gov.ae/en/services/instant-licence",
            },
            {
                "title": "FTA UAE Corporate Tax Qualifying Free Zone Person Notice",
                "snippet": "Cabinet Decision clarifying 0% corporate tax qualifying income for Free Zone companies.",
                "url": "https://tax.gov.ae/en/corporate-tax",
            },
        ]

    async def search_regulatory_sources(
        self, query: str, jurisdiction: str | None = None
    ) -> list[dict[str, Any]]:
        return self.snippets


@pytest.fixture
def repo() -> PostgresBusinessProfileRepository:
    return PostgresBusinessProfileRepository()


@pytest.fixture
def mock_search() -> MockRegulatorySearch:
    return MockRegulatorySearch()


@pytest.fixture
def sample_profiles(
    repo: PostgresBusinessProfileRepository,
) -> dict[str, StartupProfile]:
    profile_mainland = StartupProfile(
        company_name="Mainland Logistics LLC",
        industry_sector="Logistics",
        business_activity="Freight Forwarding and Distribution",
        revenue_model="B2B_Services",
        uae_local_trade=True,
        visa_quota_needed=5,
        office_preference="PhysicalOffice",
        founders_summary="Mainland Trade Founders",
    )
    profile_freezone = StartupProfile(
        company_name="Cloud AI FZ-LLC",
        industry_sector="Technology",
        business_activity="AI Consulting and Software Development",
        revenue_model="B2B_SaaS",
        uae_local_trade=False,
        visa_quota_needed=3,
        office_preference="FlexiDesk",
        founders_summary="FreeZone Tech Founders",
    )
    # Save to repo
    import asyncio

    asyncio.run(repo.save_startup_profile(profile_mainland, "ws_mainland_01"))
    asyncio.run(repo.save_startup_profile(profile_freezone, "ws_freezone_02"))

    return {"ws_mainland_01": profile_mainland, "ws_freezone_02": profile_freezone}


@pytest.mark.asyncio
class TestRegulatoryMonitorService:
    """Tests for change detection, hash comparison, and alert generation."""

    async def test_initial_detection_creates_alerts_and_stores_hashes(
        self,
        repo: PostgresBusinessProfileRepository,
        mock_search: MockRegulatorySearch,
        sample_profiles: dict[str, StartupProfile],
    ):
        monitor = RegulatoryUpdateMonitor(
            search_port=mock_search,
            repository=repo,
            topics=[DEFAULT_REGULATORY_TOPICS[0]],
        )

        alerts = await monitor.check_for_updates()

        # Should generate alerts on initial run
        assert len(alerts) >= 2
        alert_titles = [a.change_summary for a in alerts]
        assert any("Instant Licence" in t for t in alert_titles)
        assert any("Corporate Tax" in t for t in alert_titles)

        # Hashes should be stored in repo
        stored_alerts = await repo.get_regulatory_alerts()
        assert len(stored_alerts) == len(alerts)

    async def test_identical_subsequent_run_generates_zero_alerts(
        self,
        repo: PostgresBusinessProfileRepository,
        mock_search: MockRegulatorySearch,
        sample_profiles: dict[str, StartupProfile],
    ):
        monitor = RegulatoryUpdateMonitor(
            search_port=mock_search,
            repository=repo,
            topics=[DEFAULT_REGULATORY_TOPICS[0]],
        )

        # First run detects changes and populates hashes
        alerts_first_run = await monitor.check_for_updates()
        assert len(alerts_first_run) >= 2

        # Second run with identical snippets should detect 0 changes
        alerts_second_run = await monitor.check_for_updates()
        assert len(alerts_second_run) == 0

    async def test_material_content_change_triggers_new_alert(
        self,
        repo: PostgresBusinessProfileRepository,
        mock_search: MockRegulatorySearch,
        sample_profiles: dict[str, StartupProfile],
    ):
        monitor = RegulatoryUpdateMonitor(
            search_port=mock_search,
            repository=repo,
            topics=[DEFAULT_REGULATORY_TOPICS[0]],
        )

        # First run
        await monitor.check_for_updates()

        # Mutate the regulatory snippet content
        mock_search.snippets = [
            {
                "title": "Dubai DET Instant Licence Eligibility Expansion",
                "snippet": "URGENT UPDATE: DET adds 50 additional trading activities to Instant Licence program.",
                "url": "https://dubaidet.gov.ae/en/services/instant-licence",
            }
        ]

        # Second run detects modified hash
        new_alerts = await monitor.check_for_updates()
        assert len(new_alerts) == 1
        assert "URGENT UPDATE" in new_alerts[0].change_summary

    async def test_workspace_impact_filtering(
        self,
        repo: PostgresBusinessProfileRepository,
        sample_profiles: dict[str, StartupProfile],
    ):
        # Tax update impacts both mainland and free zone
        tax_search = MockRegulatorySearch(
            [
                {
                    "title": "FTA Corporate Tax Ruling",
                    "snippet": "Federal Corporate Tax 9% threshold applied to all UAE legal entities.",
                    "url": "https://tax.gov.ae",
                }
            ]
        )
        monitor = RegulatoryUpdateMonitor(
            search_port=tax_search,
            repository=repo,
            topics=[
                {
                    "query": "Corporate Tax",
                    "authority": "FTA",
                    "jurisdiction": "Federal_UAE",
                    "category": "tax",
                    "default_url": "https://tax.gov.ae",
                }
            ],
        )

        alerts = await monitor.check_for_updates()
        assert len(alerts) == 1
        # Should impact both active workspaces
        assert "ws_mainland_01" in alerts[0].impacted_workspace_ids
        assert "ws_freezone_02" in alerts[0].impacted_workspace_ids


@pytest.mark.asyncio
class TestRegulatoryMonitorWorker:
    """Tests for monitor background worker with Langfuse tracing and flush invocation."""

    async def test_worker_invokes_monitor_and_flushes_langfuse(self):
        mock_monitor = MagicMock(spec=RegulatoryUpdateMonitor)
        mock_alert = RegulatoryAlert(
            alert_id="alert_test_01",
            authority="DET",
            change_summary="DET updated license categories.",
            effective_date="2026-11-20",
            source_url="https://dubaidet.gov.ae",
            impacted_workspace_ids=["ws_1"],
        )
        mock_monitor.check_for_updates = AsyncMock(return_value=[mock_alert])

        mock_observability = MagicMock()
        mock_observability.flush = AsyncMock()

        worker = RegulatoryMonitorWorker(
            monitor=mock_monitor,
            observability=mock_observability,
        )

        alerts = await worker.run_once()

        assert alerts == [mock_alert]
        mock_monitor.check_for_updates.assert_awaited_once()
        mock_observability.flush.assert_awaited_once()

    async def test_worker_flushes_even_when_monitor_fails(self):
        mock_monitor = MagicMock(spec=RegulatoryUpdateMonitor)
        mock_monitor.check_for_updates = AsyncMock(
            side_effect=RuntimeError("Search service timeout")
        )

        mock_observability = MagicMock()
        mock_observability.flush = AsyncMock()

        worker = RegulatoryMonitorWorker(
            monitor=mock_monitor,
            observability=mock_observability,
        )

        with pytest.raises(RuntimeError, match="Search service timeout"):
            await worker.run_once()

        # Flush must still be called in finally block
        mock_observability.flush.assert_awaited_once()


class TestA2UIAlertBannerSurfaceAndAPI:
    """Tests for A2UI alert banner surface builder and GET /v1/workspaces/{id}/alerts endpoint."""

    def test_build_regulatory_alert_surface(self):
        builder = A2UISurfaceBuilder()
        alerts = [
            RegulatoryAlert(
                alert_id="alert_101",
                authority="Dubai Economy & Tourism (DET)",
                change_summary="Mainland 100% foreign ownership extended to commercial logistics.",
                effective_date="2026-11-20",
                source_url="https://dubaidet.gov.ae",
                impacted_workspace_ids=["ws_100"],
            ),
            RegulatoryAlert(
                alert_id="alert_102",
                authority="Federal Tax Authority (FTA)",
                change_summary="Qualifying Free Zone Person 0% tax clarification issued.",
                effective_date="2026-11-20",
                source_url="https://tax.gov.ae",
                impacted_workspace_ids=["ws_100"],
            ),
        ]

        messages = builder.build_regulatory_alert_surface(
            alerts=alerts,
            surface_id="test_alerts_surface",
        )

        assert len(messages) == 2
        components = messages[1].update_components.components
        comp_map = {c["id"]: c for c in components}

        assert "alert_root" in comp_map
        assert "alert_title" in comp_map
        assert "card_alert_0" in comp_map
        assert "badge_alert_0" in comp_map
        assert comp_map["badge_alert_0"]["variant"] == "warning"
        assert "source_alert_0" in comp_map
        assert comp_map["source_alert_0"]["component"] == "MarkdownViewer"

        wire_dicts = builder.to_wire_dicts(messages)
        assert wire_dicts[0]["createSurface"]["surfaceId"] == "test_alerts_surface"
        assert len(wire_dicts[1]["updateComponents"]["components"]) == len(components)

    def test_get_workspace_alerts_api_endpoint(self):
        container = Container()
        alert = RegulatoryAlert(
            alert_id="alert_api_99",
            authority="Federal Tax Authority",
            change_summary="Mandatory e-invoicing Phase 1 effective date announced.",
            effective_date="2026-11-20",
            source_url="https://tax.gov.ae/e-invoicing",
            impacted_workspace_ids=["ws_target_123"],
        )
        import asyncio

        asyncio.run(container.repository.save_regulatory_alert(alert))

        app.dependency_overrides[get_container] = lambda: container
        client = TestClient(app)

        # Query endpoint for impacted workspace
        resp = client.get("/v1/workspaces/ws_target_123/alerts")
        assert resp.status_code == 200
        data = resp.json()

        assert data["workspace_id"] == "ws_target_123"
        assert data["alert_count"] == 1
        assert data["alerts"][0]["alert_id"] == "alert_api_99"
        assert len(data["a2ui_surface"]) == 2  # createSurface + updateComponents

        # Query endpoint for unaffected workspace
        resp_empty = client.get("/v1/workspaces/ws_unaffected/alerts")
        assert resp_empty.status_code == 200
        data_empty = resp_empty.json()
        assert data_empty["alert_count"] == 0
        assert data_empty["a2ui_surface"] == []

        app.dependency_overrides.clear()
