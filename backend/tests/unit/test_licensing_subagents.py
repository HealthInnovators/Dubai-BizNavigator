"""Unit tests for UAE regulatory search tool and licensing subagents.

Verifies:
1. Search domain filtering restricted to authoritative UAE portals.
2. Structured snippet extraction with exact URLs and titles.
3. Licensing Strategist subagent specification and scoring instructions.
4. Regulatory Researcher subagent compliance coverage (Corporate Tax, VAT, UBO, AML).
5. Validation of output matching domain LicensingRecommendation entity.
"""

from unittest.mock import MagicMock

import pytest

from app.domain.entities import LicensingRecommendation
from app.infrastructure.agents.subagents.licensing_strategist import (
    LICENSING_STRATEGIST_SYSTEM_PROMPT,
    get_licensing_strategist_subagent,
)
from app.infrastructure.agents.subagents.regulatory_researcher import (
    REGULATORY_RESEARCHER_SYSTEM_PROMPT,
    get_regulatory_researcher_subagent,
)
from app.infrastructure.agents.tools.regulatory_search import (
    UAE_AUTHORITATIVE_DOMAINS,
    TavilyRegulatorySearchAdapter,
    create_regulatory_search_tool,
)


class TestTavilyRegulatorySearchAdapter:
    """Tests for TavilyRegulatorySearchAdapter and domain filtering."""

    def test_default_include_domains_contains_authoritative_uae_portals(self) -> None:
        adapter = TavilyRegulatorySearchAdapter()
        required_portals = [
            "dubaidet.gov.ae",
            "investindubai.gov.ae",
            "dmcc.ae",
            "dubaichamberdigital.com",
        ]
        for portal in required_portals:
            assert portal in adapter.include_domains, f"Portal {portal} missing from search whitelist"

    @pytest.mark.asyncio
    async def test_search_calls_client_with_restricted_domains(self) -> None:
        mock_client = MagicMock()
        mock_client.search.return_value = {
            "results": [
                {
                    "title": "Dubai DET Commercial Licensing Regulations",
                    "url": "https://dubaidet.gov.ae/en/business/commercial-licensing",
                    "content": "Foreign investors enjoy 100% full foreign ownership across 1000+ commercial activities.",
                    "score": 0.99,
                },
                {
                    "title": "Invest in Dubai - Instant Trade License Guide",
                    "url": "https://investindubai.gov.ae/en/start-your-business",
                    "content": "Issue commercial licenses without an initial office lease contract in Year 1.",
                    "score": 0.95,
                },
            ]
        }

        adapter = TavilyRegulatorySearchAdapter(client=mock_client)
        results = await adapter.search_regulatory_sources(
            query="software consulting and instant licence", jurisdiction="DET"
        )

        mock_client.search.assert_called_once()
        _, kwargs = mock_client.search.call_args
        assert kwargs["include_domains_mode"] == "restrict"
        assert set(UAE_AUTHORITATIVE_DOMAINS).issubset(set(kwargs["include_domains"]))
        assert "DET" in kwargs["query"]

        assert len(results) == 2
        assert results[0]["title"] == "Dubai DET Commercial Licensing Regulations"
        assert results[0]["url"] == "https://dubaidet.gov.ae/en/business/commercial-licensing"
        assert results[0]["authority"] == "Dubai Department of Economy and Tourism (DET)"
        assert results[1]["url"] == "https://investindubai.gov.ae/en/start-your-business"

    @pytest.mark.asyncio
    async def test_fallback_search_returns_authoritative_urls(self) -> None:
        # Without API key or client, fallback returns verified UAE URLs
        adapter = TavilyRegulatorySearchAdapter(api_key=None, client=None)
        results = await adapter.search_regulatory_sources(query="general commercial trade")

        assert len(results) >= 2
        urls = [r["url"] for r in results]
        assert any("dubaidet.gov.ae" in u for u in urls)
        assert any("investindubai.gov.ae" in u for u in urls)
        for item in results:
            assert item["title"] != ""
            assert item["url"].startswith("https://")

    def test_create_regulatory_search_tool_attributes(self) -> None:
        search_tool = create_regulatory_search_tool()
        assert search_tool.name == "search_uae_regulations"
        assert "authoritative UAE regulatory portals" in search_tool.description


class TestLicensingStrategistSubagent:
    """Tests for licensing-strategist subagent specification."""

    def test_spec_attributes_and_name(self) -> None:
        subagent = get_licensing_strategist_subagent()
        assert subagent["name"] == "licensing-strategist"
        assert "licensing matrix" in subagent["description"].lower()
        assert len(subagent["tools"]) >= 1

    def test_prompt_covers_mainland_det_and_instant_licence(self) -> None:
        prompt = LICENSING_STRATEGIST_SYSTEM_PROMPT
        assert "DET Normal Commercial Licence" in prompt
        assert "DET Instant Licence" in prompt
        assert "100% Foreign Ownership" in prompt
        assert "/workspace/startup_profile.json" in prompt
        assert "/workspace/licensing_matrix.md" in prompt

    def test_prompt_covers_free_zones_and_mainland_restrictions(self) -> None:
        prompt = LICENSING_STRATEGIST_SYSTEM_PROMPT
        assert "DMCC" in prompt
        assert "DIFC" in prompt
        assert "Dubai Internet City" in prompt
        assert "Mainland Trading Restrictions" in prompt
        assert "visa quotas" in prompt.lower()
        assert "[Source](URL)" in prompt


class TestRegulatoryResearcherSubagent:
    """Tests for regulatory-researcher subagent specification."""

    def test_spec_attributes_and_name(self) -> None:
        subagent = get_regulatory_researcher_subagent()
        assert subagent["name"] == "regulatory-researcher"
        assert "compliance" in subagent["description"].lower()

    def test_prompt_covers_uae_corporate_tax_and_vat(self) -> None:
        prompt = REGULATORY_RESEARCHER_SYSTEM_PROMPT
        # Corporate Tax checks
        assert "Federal Decree-Law No. 47 of 2022" in prompt
        assert "9%" in prompt
        assert "375,000" in prompt
        assert "Qualifying Free Zone Person" in prompt
        assert "Small Business Relief" in prompt
        # VAT checks
        assert "Federal Decree-Law No. 8 of 2017" in prompt
        assert "5%" in prompt

    def test_prompt_covers_ubo_aml_and_external_approvals(self) -> None:
        prompt = REGULATORY_RESEARCHER_SYSTEM_PROMPT
        # UBO & AML
        assert "Cabinet Resolution No. 109 of 2020" in prompt
        assert "goAML" in prompt
        assert "DNFBP" in prompt
        # External regulatory approvals
        assert "VARA" in prompt
        assert "CBUAE" in prompt
        assert "KHDA" in prompt
        assert "DHA" in prompt


class TestStructuredRecommendationIntegration:
    """Verify structured recommendation output satisfies domain LicensingRecommendation constraints."""

    def test_simulated_recommendation_validates_domain_entity(self) -> None:
        # Simulate structured output generated from licensing_strategist analysis
        simulated_output = {
            "pathway": "Mainland_DET",
            "recommended_authority": "Dubai Department of Economy and Tourism (DET)",
            "licence_type": "Commercial - Instant Licence",
            "estimated_cost_aed_min": 16500.0,
            "estimated_cost_aed_max": 23500.0,
            "visa_capacity": 4,
            "mainland_trading_notes": (
                "Eligible for 100% foreign ownership. Instant Licence exempts initial lease/Ejari for Year 1. "
                "Unrestricted commercial trade across the entire UAE mainland."
            ),
            "source_urls": [
                "https://dubaidet.gov.ae/en/business/commercial-licensing",
                "https://investindubai.gov.ae/en/start-your-business",
            ],
        }

        # Validate with pure domain model
        recommendation = LicensingRecommendation(**simulated_output)
        assert recommendation.pathway == "Mainland_DET"
        assert recommendation.recommended_authority == "Dubai Department of Economy and Tourism (DET)"
        assert recommendation.estimated_cost_aed_max >= recommendation.estimated_cost_aed_min
        assert len(recommendation.source_urls) == 2
        for url in recommendation.source_urls:
            assert url.startswith("https://")
