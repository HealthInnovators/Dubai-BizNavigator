"""A2UI Protocol integration for declarative streaming surfaces."""

from app.interfaces.a2ui.catalog import (
    BIZNAVIGATOR_CATALOG_ID,
    ApprovalGateCardWidget,
    BadgeWidget,
    ButtonWidget,
    CardWidget,
    ColumnWidget,
    DataTableWidget,
    MarkdownViewerWidget,
    RowWidget,
    SelectWidget,
    TextFieldWidget,
    TextWidget,
    create_biznavigator_catalog,
    get_biznavigator_catalog,
    get_biznavigator_validator,
    validate_a2ui_component,
    validate_a2ui_components,
)
from app.interfaces.a2ui.sse_streamer import (
    A2UISSEStreamer,
    create_sse_response,
    format_sse_chunk,
    multiplex_agent_and_a2ui_stream,
)
from app.interfaces.a2ui.surface_builder import (
    A2UISurfaceBuilder,
    A2UITransportMessage,
)

__all__ = [
    "ApprovalGateCardWidget",
    "BadgeWidget",
    "BIZNAVIGATOR_CATALOG_ID",
    "ButtonWidget",
    "CardWidget",
    "ColumnWidget",
    "DataTableWidget",
    "MarkdownViewerWidget",
    "RowWidget",
    "SelectWidget",
    "TextFieldWidget",
    "TextWidget",
    "create_biznavigator_catalog",
    "get_biznavigator_catalog",
    "get_biznavigator_validator",
    "validate_a2ui_component",
    "validate_a2ui_components",
    "A2UISurfaceBuilder",
    "A2UITransportMessage",
    "A2UISSEStreamer",
    "create_sse_response",
    "format_sse_chunk",
    "multiplex_agent_and_a2ui_stream",
]
