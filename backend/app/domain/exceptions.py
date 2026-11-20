"""Pure domain exceptions for Dubai BizNavigator."""


class DomainError(Exception):
    """Base domain exception."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class DomainValidationError(DomainError):
    """Raised when domain entity or value object validation rules are violated."""


class BusinessRuleViolationError(DomainError):
    """Raised when a business invariant is violated."""


class JurisdictionConflictError(DomainError):
    """Raised when requested business activity conflicts with selected jurisdiction."""


class HITLApprovalRequiredError(DomainError):
    """Raised when an operation requires Human-In-The-Loop approval before proceeding."""


class ExternalIntegrationError(DomainError):
    """Raised when an external regulatory or banking integration fails."""


class EntityNotFoundError(DomainError):
    """Raised when a requested domain entity does not exist."""


class InvalidJurisdictionError(BusinessRuleViolationError):
    """Raised when an invalid UAE/Dubai jurisdiction is specified."""
