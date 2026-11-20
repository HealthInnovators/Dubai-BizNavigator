"""Dependency injection container wiring Clean Architecture layers."""

from functools import lru_cache

from app.application.coordinators.workflow_coordinator import (
    BusinessSetupWorkflowCoordinator,
)
from app.application.regulatory_monitor import RegulatoryUpdateMonitor
from app.application.use_cases import (
    ApproveHITLGateUseCase,
    GetWorkspaceArtifactsUseCase,
    InitializeBusinessProfileUseCase,
    ProcessUserMessageUseCase,
    StartSetupSessionUseCase,
)
from app.domain.ports import (
    BankingServicePort,
    BankingWorkflowPort,
    RegulatorySearchPort,
    SearchServicePort,
    WorkspaceRepositoryPort,
)
from app.infrastructure.adapters.banking_api import BankingAPIAdapter
from app.infrastructure.adapters.tavily_search import TavilySearchAdapter
from app.infrastructure.agents.orchestrator import DeepAgentsOrchestrator
from app.infrastructure.agents.tools.regulatory_search import (
    TavilyRegulatorySearchAdapter,
)
from app.infrastructure.banking.corporate_banking_adapter import CorporateBankingAdapter
from app.infrastructure.config import Settings, settings
from app.infrastructure.database.postgres_adapter import PostgresBusinessProfileRepository
from app.infrastructure.observability.langfuse_adapter import LangfuseObservabilityAdapter
from app.infrastructure.workers.monitor_worker import RegulatoryMonitorWorker
from app.interfaces.a2ui.surface_builder import A2UISurfaceBuilder


class Container:
    """Dependency injection container for the application."""

    def __init__(self, app_settings: Settings = settings) -> None:
        self.settings = app_settings

        # Infrastructure adapters
        self.repository: WorkspaceRepositoryPort = PostgresBusinessProfileRepository(
            dsn=self.settings.DATABASE_URL
        )
        self.search_service: SearchServicePort = TavilySearchAdapter(
            api_key=self.settings.TAVILY_API_KEY
        )
        self.banking_service: BankingServicePort = BankingAPIAdapter()
        self.corporate_banking: BankingWorkflowPort = CorporateBankingAdapter(
            base_url=self.settings.BANKING_API_BASE_URL,
            api_key=self.settings.BANKING_API_KEY,
            webhook_secret=self.settings.BANKING_WEBHOOK_SECRET,
            sandbox_mode=self.settings.BANKING_SANDBOX_MODE,
        )
        self.observability = LangfuseObservabilityAdapter(
            public_key=self.settings.LANGFUSE_PUBLIC_KEY,
            secret_key=self.settings.LANGFUSE_SECRET_KEY,
            base_url=self.settings.LANGFUSE_BASE_URL,
        )
        self.surface_builder = A2UISurfaceBuilder()
        self.orchestrator = DeepAgentsOrchestrator(
            langfuse_adapter=self.observability,
        )

        # Application services / Use cases
        self.initialize_profile_use_case = InitializeBusinessProfileUseCase(
            repository=self.repository
        )
        self.workflow_coordinator = BusinessSetupWorkflowCoordinator(
            repository=self.repository,
            search_service=self.search_service,
            banking_service=self.banking_service,
        )

        # Modern autonomous setup use cases
        self.start_session_use_case = StartSetupSessionUseCase(
            repository=self.repository
        )
        self.process_message_use_case = ProcessUserMessageUseCase(
            orchestrator=self.orchestrator,
            repository=self.repository,
            surface_builder=self.surface_builder,
        )
        self.approve_hitl_use_case = ApproveHITLGateUseCase(
            orchestrator=self.orchestrator,
            repository=self.repository,
            surface_builder=self.surface_builder,
        )
        self.get_artifacts_use_case = GetWorkspaceArtifactsUseCase(
            repository=self.repository
        )

        # Regulatory update monitor and worker
        self.regulatory_search: RegulatorySearchPort = TavilyRegulatorySearchAdapter(
            api_key=self.settings.TAVILY_API_KEY
        )
        self.regulatory_monitor = RegulatoryUpdateMonitor(
            search_port=self.regulatory_search,
            repository=self.repository,
        )
        self.monitor_worker = RegulatoryMonitorWorker(
            monitor=self.regulatory_monitor,
            observability=self.observability,
        )


@lru_cache
def get_container() -> Container:
    """Singleton provider for DI container."""
    return Container()
