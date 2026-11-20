"""Pure Clean Architecture Domain Layer for Dubai BizNavigator.

Contains entities, value objects, domain exceptions, and port interfaces.
Zero dependencies on FastAPI, LangChain, Langfuse, or A2UI.
"""

from app.domain.entities import (
    BankingReadinessPackage,
    BusinessProfile,
    LicensingRecommendation,
    RegistrationPayload,
    RegulatoryAlert,
    StartupProfile,
)
from app.domain.exceptions import (
    BusinessRuleViolationError,
    DomainError,
    DomainValidationError,
    EntityNotFoundError,
    ExternalIntegrationError,
    HITLApprovalRequiredError,
    InvalidJurisdictionError,
    JurisdictionConflictError,
)
from app.domain.ports import (
    AgentOrchestratorPort,
    BankingServicePort,
    BankingWorkflowPort,
    BusinessProfileRepositoryPort,
    ObservabilityPort,
    RegulatorySearchPort,
    SearchServicePort,
    WorkspaceRepositoryPort,
)
from app.domain.value_objects.license_type import (
    Jurisdiction,
    JurisdictionType,
    LicenseCategory,
)

__all__ = [
    # Entities
    "BankingReadinessPackage",
    "BusinessProfile",
    "LicensingRecommendation",
    "RegistrationPayload",
    "RegulatoryAlert",
    "StartupProfile",
    # Exceptions
    "BusinessRuleViolationError",
    "DomainError",
    "DomainValidationError",
    "EntityNotFoundError",
    "ExternalIntegrationError",
    "HITLApprovalRequiredError",
    "InvalidJurisdictionError",
    "JurisdictionConflictError",
    # Ports
    "AgentOrchestratorPort",
    "BankingServicePort",
    "BankingWorkflowPort",
    "BusinessProfileRepositoryPort",
    "ObservabilityPort",
    "RegulatorySearchPort",
    "SearchServicePort",
    "WorkspaceRepositoryPort",
    # Value Objects
    "Jurisdiction",
    "JurisdictionType",
    "LicenseCategory",
]
