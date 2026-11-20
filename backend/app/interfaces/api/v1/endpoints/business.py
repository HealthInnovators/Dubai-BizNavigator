"""Business formation and SSE stream endpoints."""

from collections.abc import AsyncGenerator

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse

from app.application.dtos.business_dto import (
    BusinessProfileResponseDTO,
    CreateBusinessProfileDTO,
)
from app.domain.exceptions import DomainError
from app.interfaces.container import Container, get_container
from app.interfaces.serializers.a2ui_serializer import A2UIMessageSerializer
from app.interfaces.sse.sse_handler import format_sse_message

router = APIRouter(prefix="/business", tags=["Business"])


@router.post(
    "/profile",
    response_model=BusinessProfileResponseDTO,
    status_code=status.HTTP_201_CREATED,
)
async def create_profile(
    payload: CreateBusinessProfileDTO,
    container: Container = Depends(get_container),
) -> BusinessProfileResponseDTO:
    """Initialize a business formation profile."""
    try:
        return await container.initialize_profile_use_case.execute(payload)
    except DomainError as err:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(err),
        ) from err


@router.get("/stream/{profile_id}")
async def stream_formation_progress(
    profile_id: str,
    container: Container = Depends(get_container),
) -> StreamingResponse:
    """Stream business setup agent progress as Server-Sent Events with A2UI payloads."""

    async def event_generator() -> AsyncGenerator[str, None]:
        coordinator = container.workflow_coordinator
        async for event in coordinator.stream_workflow_progress(profile_id):
            surface = A2UIMessageSerializer.create_progress_surface(
                surface_id=f"progress-{profile_id}",
                current_step=event.step,
                progress_percentage=100 if event.status == "completed" else 50,
                log_message=event.message,
            )
            yield format_sse_message(
                event="a2ui_surface",
                data={
                    "event": event.model_dump(),
                    "surface": surface,
                },
            )

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
