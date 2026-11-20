"""Agent workflow coordinator orchestrating multi-step formation tasks."""

from collections.abc import AsyncGenerator

from app.application.dtos.business_dto import WorkflowEventDTO
from app.domain.ports import (
    BankingServicePort,
    BusinessProfileRepositoryPort,
    SearchServicePort,
)


class BusinessSetupWorkflowCoordinator:
    """Coordinates business setup stages across agents and domain ports."""

    def __init__(
        self,
        repository: BusinessProfileRepositoryPort,
        search_service: SearchServicePort,
        banking_service: BankingServicePort,
    ) -> None:
        self.repository = repository
        self.search_service = search_service
        self.banking_service = banking_service

    async def stream_workflow_progress(
        self, profile_id: str
    ) -> AsyncGenerator[WorkflowEventDTO, None]:
        """Yield workflow execution events simulating / streaming steps."""
        yield WorkflowEventDTO(
            step="validation",
            status="started",
            message="Validating business activity against Dubai DED regulations...",
        )

        profile = await self.repository.get_by_id(profile_id)
        if not profile:
            yield WorkflowEventDTO(
                step="validation",
                status="failed",
                message=f"Business profile {profile_id} not found.",
            )
            return

        yield WorkflowEventDTO(
            step="jurisdiction_matching",
            status="in_progress",
            message=f"Searching optimal zones for activity in {profile.business_name}...",
        )

        search_results = await self.search_service.search_regulations(
            query=profile.activity_description,
            jurisdiction=profile.jurisdiction.authority_code if profile.jurisdiction else None,
        )

        yield WorkflowEventDTO(
            step="banking_eligibility",
            status="in_progress",
            message="Assessing UAE corporate bank account readiness...",
            payload={"regulatory_hits": len(search_results)},
        )

        banking_status = await self.banking_service.evaluate_eligibility(
            business_profile_id=profile_id,
            jurisdiction_code=profile.jurisdiction.authority_code if profile.jurisdiction else "DED",
            activity_code="COMMERCIAL",
        )

        yield WorkflowEventDTO(
            step="complete",
            status="completed",
            message="Setup plan and banking feasibility compiled successfully.",
            payload={"banking": banking_status},
        )
