"""Data Transfer Objects for application use cases."""

from pydantic import BaseModel, Field


class CreateBusinessProfileDTO(BaseModel):
    """Payload to initiate a Dubai business setup profile."""

    business_name: str = Field(..., min_length=2, max_length=150)
    activity_description: str = Field(..., min_length=5, max_length=1000)
    jurisdiction_type: str = Field(..., pattern="^(mainland|freezone|offshore)$")
    authority_code: str = Field(..., min_length=2, max_length=50)
    license_category: str = Field(..., pattern="^(commercial|professional|industrial|tourism)$")


class BusinessProfileResponseDTO(BaseModel):
    """Response payload for business profiles."""

    id: str
    business_name: str
    activity_description: str
    jurisdiction_type: str | None = None
    authority_code: str | None = None
    license_category: str | None = None
    is_ready_for_application: bool
    created_at: str


class WorkflowEventDTO(BaseModel):
    """Event emitted during agent workflow orchestration."""

    step: str
    status: str
    message: str
    payload: dict = Field(default_factory=dict)
