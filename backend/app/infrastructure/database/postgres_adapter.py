"""PostgreSQL adapter implementing BusinessProfileRepositoryPort."""

from app.domain.entities import (
    BankingReadinessPackage,
    BusinessProfile,
    LicensingRecommendation,
    RegistrationPayload,
    RegulatoryAlert,
    StartupProfile,
)
from app.domain.ports import WorkspaceRepositoryPort


class PostgresBusinessProfileRepository(WorkspaceRepositoryPort):
    """PostgreSQL repository adapter for business profiles and workspace entities."""

    def __init__(self, dsn: str | None = None) -> None:
        self.dsn = dsn
        self._in_memory_store: dict[str, BusinessProfile] = {}
        self._startup_profiles: dict[str, StartupProfile] = {}
        self._licensing_recommendations: dict[str, LicensingRecommendation] = {}
        self._registration_payloads: dict[str, RegistrationPayload] = {}
        self._banking_packages: dict[str, BankingReadinessPackage] = {}
        self._regulatory_alerts: list[RegulatoryAlert] = []
        self._regulatory_hashes: dict[str, str] = {}

    async def get_by_id(self, profile_id: str) -> BusinessProfile | None:
        return self._in_memory_store.get(profile_id)

    async def save(self, profile: BusinessProfile) -> BusinessProfile:
        self._in_memory_store[profile.id] = profile
        return profile

    async def save_startup_profile(
        self, profile: StartupProfile, workspace_id: str
    ) -> StartupProfile:
        profile.workspace_id = workspace_id
        self._startup_profiles[workspace_id] = profile
        return profile

    async def get_startup_profile(self, workspace_id: str) -> StartupProfile | None:
        return self._startup_profiles.get(workspace_id)

    async def save_licensing_recommendation(
        self, recommendation: LicensingRecommendation, workspace_id: str
    ) -> LicensingRecommendation:
        recommendation.workspace_id = workspace_id
        self._licensing_recommendations[workspace_id] = recommendation
        return recommendation

    async def get_licensing_recommendation(
        self, workspace_id: str
    ) -> LicensingRecommendation | None:
        return self._licensing_recommendations.get(workspace_id)

    async def save_registration_payload(
        self, payload: RegistrationPayload, workspace_id: str
    ) -> RegistrationPayload:
        payload.workspace_id = workspace_id
        self._registration_payloads[workspace_id] = payload
        return payload

    async def get_registration_payload(
        self, workspace_id: str
    ) -> RegistrationPayload | None:
        return self._registration_payloads.get(workspace_id)

    async def save_banking_readiness_package(
        self, package: BankingReadinessPackage, workspace_id: str
    ) -> BankingReadinessPackage:
        package.workspace_id = workspace_id
        self._banking_packages[workspace_id] = package
        return package

    async def get_banking_readiness_package(
        self, workspace_id: str
    ) -> BankingReadinessPackage | None:
        return self._banking_packages.get(workspace_id)

    async def save_regulatory_alert(self, alert: RegulatoryAlert) -> RegulatoryAlert:
        self._regulatory_alerts.append(alert)
        return alert

    async def get_regulatory_alerts(
        self, workspace_id: str | None = None
    ) -> list[RegulatoryAlert]:
        if workspace_id is None:
            return list(self._regulatory_alerts)
        return [
            alert
            for alert in self._regulatory_alerts
            if workspace_id in alert.impacted_workspace_ids
        ]

    async def get_all_startup_profiles(self) -> dict[str, StartupProfile]:
        return dict(self._startup_profiles)

    async def get_regulatory_hash(self, source_key: str) -> str | None:
        return self._regulatory_hashes.get(source_key)

    async def set_regulatory_hash(self, source_key: str, content_hash: str) -> None:
        self._regulatory_hashes[source_key] = content_hash
