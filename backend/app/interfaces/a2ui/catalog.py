"""BizNavigator A2UI Widget Catalog definition and validation using a2ui-core."""

from typing import Any, Literal

from a2ui.core.catalog import Catalog, ModelComponentApi
from a2ui.core.exceptions import A2uiValidationError
from a2ui.core.validation import PayloadValidator
from pydantic import BaseModel, ConfigDict, Field

BIZNAVIGATOR_CATALOG_ID = "https://dubai.biznavigator.ai/catalog/v1"
PROTOCOL_VERSION_V09 = "0.9"


class BaseWidget(BaseModel):
    """Base model for all BizNavigator A2UI components."""

    model_config = ConfigDict(extra="ignore")
    id: str


class TextWidget(BaseWidget):
    """Text display component with typography variant support."""

    component: Literal["Text"] = "Text"
    text: str
    variant: str | None = "body"


class ColumnWidget(BaseWidget):
    """Vertical layout container."""

    component: Literal["Column"] = "Column"
    children: list[str] = Field(default_factory=list)
    justify: str | None = "start"
    align: str | None = "stretch"


class RowWidget(BaseWidget):
    """Horizontal layout container."""

    component: Literal["Row"] = "Row"
    children: list[str] = Field(default_factory=list)
    justify: str | None = "start"
    align: str | None = "center"


class CardWidget(BaseWidget):
    """Card container for grouping content with optional title."""

    component: Literal["Card"] = "Card"
    child: str | None = None
    title: str | None = None
    variant: str | None = "elevated"


class DataTableWidget(BaseWidget):
    """Tabular data representation for matrix comparisons."""

    component: Literal["DataTable"] = "DataTable"
    columns: list[dict[str, Any]] = Field(default_factory=list)
    rows: list[dict[str, Any]] = Field(default_factory=list)
    title: str | None = None


class BadgeWidget(BaseWidget):
    """Status or category pill badge."""

    component: Literal["Badge"] = "Badge"
    text: str
    variant: str | None = "default"


class TextFieldWidget(BaseWidget):
    """Input field for text, numeric, and identifier data."""

    component: Literal["TextField"] = "TextField"
    label: str
    name: str
    value: str | None = None
    placeholder: str | None = None
    required: bool = False
    description: str | None = None


class SelectWidget(BaseWidget):
    """Dropdown selection input."""

    component: Literal["Select"] = "Select"
    label: str
    name: str
    options: list[dict[str, str]] = Field(default_factory=list)
    value: str | None = None
    required: bool = False


class ButtonWidget(BaseWidget):
    """Interactive trigger button with action metadata."""

    component: Literal["Button"] = "Button"
    label: str
    action: str | dict[str, Any]
    variant: str | None = "primary"
    disabled: bool = False


class ApprovalGateCardWidget(BaseWidget):
    """Interactive Human-in-the-Loop decision gate card."""

    component: Literal["ApprovalGateCard"] = "ApprovalGateCard"
    title: str
    summary: str
    payload_preview: dict[str, Any] = Field(default_factory=dict)
    approve_action: str | dict[str, Any] = "hitl_approve"
    reject_action: str | dict[str, Any] = "hitl_reject"
    status: str = "pending"


class MarkdownViewerWidget(BaseWidget):
    """Rich markdown document renderer with source citations and download links."""

    component: Literal["MarkdownViewer"] = "MarkdownViewer"
    content: str
    title: str | None = None
    source_links: list[dict[str, str]] = Field(default_factory=list)
    download_links: list[dict[str, str]] = Field(default_factory=list)


BizNavigatorWidget = (
    TextWidget
    | ColumnWidget
    | RowWidget
    | CardWidget
    | DataTableWidget
    | BadgeWidget
    | TextFieldWidget
    | SelectWidget
    | ButtonWidget
    | ApprovalGateCardWidget
    | MarkdownViewerWidget
)

WIDGET_REGISTRY: dict[str, type[BaseModel]] = {
    "Text": TextWidget,
    "Column": ColumnWidget,
    "Row": RowWidget,
    "Card": CardWidget,
    "DataTable": DataTableWidget,
    "Badge": BadgeWidget,
    "TextField": TextFieldWidget,
    "Select": SelectWidget,
    "Button": ButtonWidget,
    "ApprovalGateCard": ApprovalGateCardWidget,
    "MarkdownViewer": MarkdownViewerWidget,
}


def create_biznavigator_catalog() -> Catalog:
    """Build the official A2UI Catalog defining all BizNavigator widgets."""
    components = [
        ModelComponentApi(model_cls, name=name)
        for name, model_cls in WIDGET_REGISTRY.items()
    ]
    return Catalog(
        catalog_id=BIZNAVIGATOR_CATALOG_ID,
        protocol_version=PROTOCOL_VERSION_V09,
        components=components,
    )


# Cached singleton catalog & validator
_CATALOG_INSTANCE: Catalog | None = None
_VALIDATOR_INSTANCE: PayloadValidator | None = None


def get_biznavigator_catalog() -> Catalog:
    """Retrieve singleton instance of BizNavigator A2UI Catalog."""
    global _CATALOG_INSTANCE
    if _CATALOG_INSTANCE is None:
        _CATALOG_INSTANCE = create_biznavigator_catalog()
    return _CATALOG_INSTANCE


def get_biznavigator_validator() -> PayloadValidator:
    """Retrieve singleton instance of PayloadValidator for BizNavigator catalog."""
    global _VALIDATOR_INSTANCE
    if _VALIDATOR_INSTANCE is None:
        _VALIDATOR_INSTANCE = PayloadValidator(catalog=get_biznavigator_catalog())
    return _VALIDATOR_INSTANCE


def validate_a2ui_component(component_data: dict[str, Any]) -> None:
    """Validate a single component dictionary against the BizNavigator catalog.

    Raises:
        A2uiValidationError: If the component does not match catalog schema.
    """
    validator = get_biznavigator_validator()
    validator.validate_component(component_data)


def validate_a2ui_components(components_list: list[dict[str, Any]]) -> None:
    """Validate a list of component dictionaries against the BizNavigator catalog.

    Raises:
        A2uiValidationError: If any component does not match catalog schema.
    """
    errors: list[Any] = []
    validator = get_biznavigator_validator()
    for comp in components_list:
        try:
            validator.validate_component(comp)
        except A2uiValidationError as e:
            errors.extend(e.details)
        except Exception as e:
            errors.append(str(e))

    if errors:
        raise A2uiValidationError(
            f"Component validation failed with {len(errors)} error(s): {errors}",
            details=errors,
        )
