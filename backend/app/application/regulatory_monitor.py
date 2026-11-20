"""Application service for monitoring UAE regulatory changes and generating alerts."""

import hashlib
import logging
import uuid
from datetime import UTC, datetime
from typing import Any

from app.domain.entities import RegulatoryAlert, StartupProfile
from app.domain.ports import RegulatorySearchPort, WorkspaceRepositoryPort

logger = logging.getLogger("dubai_biznavigator.regulatory_monitor")

DEFAULT_REGULATORY_TOPICS = [
    {
        "query": "Dubai DET commercial licensing rules 100% foreign ownership instant licence updates",
        "authority": "Dubai Economy & Tourism (DET)",
        "jurisdiction": "Mainland_DET",
        "category": "licensing",
        "default_url": "https://dubaidet.gov.ae/en/services/instant-licence",
    },
    {
        "query": "UAE Federal Decree-Law Corporate Tax 9 percent Qualifying Free Zone Person rules",
        "authority": "Federal Tax Authority (FTA)",
        "jurisdiction": "Federal_UAE",
        "category": "tax",
        "default_url": "https://tax.gov.ae/en/corporate-tax",
    },
    {
        "query": "UAE Cabinet Decision Ultimate Beneficial Ownership UBO AML registration requirements",
        "authority": "Ministry of Economy (MoE)",
        "jurisdiction": "Federal_UAE",
        "category": "compliance",
        "default_url": "https://www.moec.gov.ae/en/anti-money-laundering",
    },
    {
        "query": "DMCC Free Zone trade licence regulations employment visa and flexi desk rules",
        "authority": "Dubai Multi Commodities Centre (DMCC)",
        "jurisdiction": "FreeZone",
        "category": "licensing",
        "default_url": "https://dmcc.ae/free-zone/setup-process",
    },
]


class RegulatoryUpdateMonitor:
    """Service to periodically detect regulatory changes and notify affected workspaces."""

    def __init__(
        self,
        search_port: RegulatorySearchPort,
        repository: WorkspaceRepositoryPort,
        topics: list[dict[str, Any]] | None = None,
    ) -> None:
        self.search_port = search_port
        self.repository = repository
        self.topics = topics or DEFAULT_REGULATORY_TOPICS

    async def check_for_updates(self) -> list[RegulatoryAlert]:
        """Poll official UAE sources, detect changes via hash comparison, and persist alerts."""
        generated_alerts: list[RegulatoryAlert] = []
        active_profiles = await self.repository.get_all_startup_profiles()

        for topic in self.topics:
            query = topic["query"]
            authority = topic["authority"]
            jurisdiction = topic.get("jurisdiction", "Federal_UAE")
            category = topic.get("category", "general")
            default_url = topic.get("default_url", "https://dubaidet.gov.ae")

            logger.info("Checking regulatory updates for: %s (%s)", authority, query)

            try:
                results = await self.search_port.search_regulatory_sources(
                    query=query, jurisdiction=jurisdiction
                )
            except Exception as exc:
                logger.warning(
                    "Search failed for topic %s: %s", authority, exc, exc_info=True
                )
                continue

            for item in results:
                title = item.get("title", f"{authority} Regulatory Bulletin")
                snippet = item.get("snippet", item.get("content", ""))
                url = item.get("url", default_url)

                if not snippet:
                    continue

                # Unique key identifying this regulatory source topic and URL
                source_key = f"reg_hash_{authority}_{url}"
                content_payload = f"{title.strip()}|{snippet.strip()}".encode()
                new_hash = hashlib.sha256(content_payload).hexdigest()

                stored_hash = await self.repository.get_regulatory_hash(source_key)

                # If content hash has changed or source is newly discovered
                if stored_hash is None or stored_hash != new_hash:
                    logger.info(
                        "Material regulatory update detected for %s (Key: %s)",
                        authority,
                        source_key,
                    )
                    await self.repository.set_regulatory_hash(source_key, new_hash)

                    # Determine impacted workspaces based on profile jurisdiction & activity
                    impacted_ids = self._find_impacted_workspaces(
                        profiles=active_profiles,
                        jurisdiction=jurisdiction,
                        category=category,
                        content_text=f"{title} {snippet}",
                    )

                    alert = RegulatoryAlert(
                        alert_id=f"alert_{uuid.uuid4().hex[:10]}",
                        authority=authority,
                        change_summary=f"{title}: {snippet[:280]}",
                        effective_date=datetime.now(UTC).strftime("%Y-%m-%d"),
                        source_url=url,
                        impacted_workspace_ids=impacted_ids,
                    )
                    saved_alert = await self.repository.save_regulatory_alert(alert)
                    generated_alerts.append(saved_alert)

        return generated_alerts

    def _find_impacted_workspaces(
        self,
        profiles: dict[str, StartupProfile],
        jurisdiction: str,
        category: str,
        content_text: str,
    ) -> list[str]:
        """Match regulatory change against active workspace parameters."""
        impacted: list[str] = []
        lower_content = content_text.lower()

        for ws_id, profile in profiles.items():
            # 1. Federal UAE Tax and UBO compliance updates impact ALL active Dubai workspaces
            if category in ("tax", "compliance") or jurisdiction == "Federal_UAE":
                impacted.append(ws_id)
                continue

            # 2. Mainland DET specific updates
            if jurisdiction == "Mainland_DET" and (
                profile.uae_local_trade or "mainland" in lower_content
            ):
                impacted.append(ws_id)
                continue

            # 3. Free Zone updates
            if jurisdiction == "FreeZone" and (
                not profile.uae_local_trade or "free zone" in lower_content
            ):
                impacted.append(ws_id)
                continue

            # 4. Industry sector or activity keywords
            if (
                profile.industry_sector.lower() in lower_content
                or profile.business_activity.lower() in lower_content
            ):
                impacted.append(ws_id)

        # If no specific workspace matches, attach to all active workspaces
        if not impacted and profiles:
            return list(profiles.keys())
        return impacted
