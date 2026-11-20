"""A2UI Surface Builder constructing declarative, wire-stable UI surfaces."""

from typing import Any, Literal

from a2ui.core.schema import (
    CreateSurface,
    CreateSurfaceMessage,
    UpdateComponents,
    UpdateComponentsMessage,
)
from pydantic import BaseModel

from app.domain.entities import (
    BankingReadinessPackage,
    LicensingRecommendation,
    RegistrationPayload,
    RegulatoryAlert,
    StartupProfile,
)
from app.interfaces.a2ui.catalog import (
    BIZNAVIGATOR_CATALOG_ID,
    validate_a2ui_components,
)

A2UITransportMessage = CreateSurfaceMessage | UpdateComponentsMessage


class A2UISurfaceBuilder:
    """Constructs declarative A2UI surfaces validated against BizNavigator catalog."""

    def __init__(self, catalog_id: str = BIZNAVIGATOR_CATALOG_ID) -> None:
        self.catalog_id = catalog_id

    def _wrap_messages(
        self, surface_id: str, components: list[dict[str, Any]]
    ) -> list[A2UITransportMessage]:
        """Validate components and wrap into CreateSurface and UpdateComponents messages."""
        validate_a2ui_components(components)

        create_msg = CreateSurfaceMessage(
            create_surface=CreateSurface(
                surface_id=surface_id,
                catalog_id=self.catalog_id,
            )
        )
        update_msg = UpdateComponentsMessage(
            update_components=UpdateComponents(
                surface_id=surface_id,
                components=components,
            )
        )
        return [create_msg, update_msg]

    def build_intake_form_surface(
        self,
        surface_id: str = "surface_intake_profile",
        default_profile: StartupProfile | None = None,
    ) -> list[A2UITransportMessage]:
        """Construct declarative Intake Form surface for capturing StartupProfile."""
        profile = default_profile

        components: list[dict[str, Any]] = [
            {
                "id": "intake_root",
                "component": "Column",
                "children": ["intake_title", "intake_card"],
                "justify": "start",
                "align": "stretch",
            },
            {
                "id": "intake_title",
                "component": "Text",
                "text": "Dubai Business Setup: Profile Intake",
                "variant": "title",
            },
            {
                "id": "intake_card",
                "component": "Card",
                "title": "Startup & Operational Configuration",
                "child": "intake_fields_col",
                "variant": "elevated",
            },
            {
                "id": "intake_fields_col",
                "component": "Column",
                "children": [
                    "field_company_name",
                    "field_industry_sector",
                    "field_business_activity",
                    "field_revenue_model",
                    "field_uae_local_trade",
                    "field_visa_quota_needed",
                    "field_office_preference",
                    "field_founders_summary",
                    "btn_submit_intake",
                ],
                "justify": "start",
                "align": "stretch",
            },
            {
                "id": "field_company_name",
                "component": "TextField",
                "label": "Company Name",
                "name": "company_name",
                "value": profile.company_name if profile else "",
                "placeholder": "e.g. Acme AI Solutions LLC",
                "required": True,
                "description": "Proposed legal trade name for UAE registration",
            },
            {
                "id": "field_industry_sector",
                "component": "TextField",
                "label": "Industry Sector",
                "name": "industry_sector",
                "value": profile.industry_sector if profile else "",
                "placeholder": "e.g. Artificial Intelligence / FinTech",
                "required": True,
            },
            {
                "id": "field_business_activity",
                "component": "TextField",
                "label": "Business Activity",
                "name": "business_activity",
                "value": profile.business_activity if profile else "",
                "placeholder": "e.g. Software Development & Technology Consultancy",
                "required": True,
            },
            {
                "id": "field_revenue_model",
                "component": "Select",
                "label": "Revenue Model",
                "name": "revenue_model",
                "value": profile.revenue_model if profile else "B2B_SaaS",
                "required": True,
                "options": [
                    {"value": "B2B_SaaS", "label": "B2B SaaS / Subscriptions"},
                    {"value": "Marketplace", "label": "Digital Marketplace / Platform"},
                    {"value": "Consulting", "label": "Professional Services & Consulting"},
                    {"value": "Fintech", "label": "Payment Processing / Financial Services"},
                    {"value": "ECommerce", "label": "Direct E-Commerce & Retail"},
                ],
            },
            {
                "id": "field_uae_local_trade",
                "component": "Select",
                "label": "UAE Mainland Local Trade Required?",
                "name": "uae_local_trade",
                "value": "true" if (profile and profile.uae_local_trade) else "false",
                "required": True,
                "options": [
                    {
                        "value": "true",
                        "label": "Yes — Direct mainland commercial trade within UAE",
                    },
                    {
                        "value": "false",
                        "label": "No — Cross-border, offshore, or free zone operations only",
                    },
                ],
            },
            {
                "id": "field_visa_quota_needed",
                "component": "TextField",
                "label": "Visa Quota Needed",
                "name": "visa_quota_needed",
                "value": str(profile.visa_quota_needed) if profile else "3",
                "placeholder": "e.g. 5",
                "required": False,
                "description": "Estimated employee and investor residence visas required",
            },
            {
                "id": "field_office_preference",
                "component": "Select",
                "label": "Office Preference",
                "name": "office_preference",
                "value": profile.office_preference if profile else "FlexiDesk",
                "required": True,
                "options": [
                    {"value": "FlexiDesk", "label": "Flexi Desk / Smart Desk (Cost Effective)"},
                    {"value": "PhysicalOffice", "label": "Dedicated Physical Office (Leased Ejari)"},
                    {"value": "Warehousing", "label": "Industrial Warehouse / Storage Unit"},
                    {"value": "None", "label": "Virtual Office (Eligible Free Zones)"},
                ],
            },
            {
                "id": "field_founders_summary",
                "component": "TextField",
                "label": "Founders Summary",
                "name": "founders_summary",
                "value": profile.founders_summary if profile else "",
                "placeholder": "e.g. 2 Co-founders (German & British, resident in Dubai)",
                "required": False,
            },
            {
                "id": "btn_submit_intake",
                "component": "Button",
                "label": "Analyze & Generate Licensing Strategy",
                "action": {
                    "event": "submit_intake_profile",
                    "surface_id": surface_id,
                },
                "variant": "primary",
            },
        ]

        return self._wrap_messages(surface_id, components)

    def build_licensing_matrix_surface(
        self,
        recommendations: list[LicensingRecommendation],
        surface_id: str = "surface_licensing_matrix",
    ) -> list[A2UITransportMessage]:
        """Construct comparative Licensing Matrix surface with DataTable and Cards."""
        columns = [
            {"key": "pathway", "label": "Jurisdiction Pathway"},
            {"key": "authority", "label": "Authority"},
            {"key": "licence_type", "label": "Licence Type"},
            {"key": "cost_range", "label": "Est. Cost (AED)"},
            {"key": "visa_capacity", "label": "Visa Capacity"},
            {"key": "mainland_trade", "label": "Mainland Trading"},
        ]

        rows = []
        for r in recommendations:
            rows.append(
                {
                    "pathway": r.pathway,
                    "authority": r.recommended_authority,
                    "licence_type": r.licence_type,
                    "cost_range": f"{r.estimated_cost_aed_min:,} - {r.estimated_cost_aed_max:,}",
                    "visa_capacity": r.visa_capacity,
                    "mainland_trade": (
                        "Direct Mainland (100% Foreign Ownership)"
                        if r.pathway == "Mainland_DET"
                        else "Free Zone / Mainland via Local Distributor"
                    ),
                }
            )

        root_children = ["licensing_title", "licensing_datatable"]
        card_components: list[dict[str, Any]] = []

        for idx, rec in enumerate(recommendations):
            card_id = f"card_rec_{idx}"
            col_id = f"col_rec_{idx}"
            badge_id = f"badge_rec_{idx}"
            notes_id = f"notes_rec_{idx}"
            sources_id = f"sources_rec_{idx}"

            root_children.append(card_id)

            source_bullets = "\n".join([f"- [{url}]({url})" for url in rec.source_urls])
            source_content = (
                f"### Verified Legal References\n{source_bullets}"
                if source_bullets
                else "No external sources cited."
            )

            card_components.extend(
                [
                    {
                        "id": card_id,
                        "component": "Card",
                        "title": f"Pathway Evaluation: {rec.recommended_authority} ({rec.pathway})",
                        "child": col_id,
                        "variant": "elevated",
                    },
                    {
                        "id": col_id,
                        "component": "Column",
                        "children": [badge_id, notes_id, sources_id],
                        "justify": "start",
                        "align": "stretch",
                    },
                    {
                        "id": badge_id,
                        "component": "Badge",
                        "text": rec.pathway,
                        "variant": "success" if rec.pathway == "Mainland_DET" else "info",
                    },
                    {
                        "id": notes_id,
                        "component": "Text",
                        "text": f"Mainland Trading & Operational Notes: {rec.mainland_trading_notes}",
                        "variant": "body",
                    },
                    {
                        "id": sources_id,
                        "component": "MarkdownViewer",
                        "title": "Regulatory Citations",
                        "content": source_content,
                        "source_links": [
                            {"title": f"Source {s_idx + 1}", "url": url}
                            for s_idx, url in enumerate(rec.source_urls)
                        ],
                    },
                ]
            )

        components: list[dict[str, Any]] = [
            {
                "id": "licensing_root",
                "component": "Column",
                "children": root_children,
                "justify": "start",
                "align": "stretch",
            },
            {
                "id": "licensing_title",
                "component": "Text",
                "text": "Dubai Jurisdiction & Licensing Comparison Matrix",
                "variant": "title",
            },
            {
                "id": "licensing_datatable",
                "component": "DataTable",
                "title": "Pathway Breakdown",
                "columns": columns,
                "rows": rows,
            },
            *card_components,
        ]

        return self._wrap_messages(surface_id, components)

    def build_hitl_approval_surface(
        self,
        payload_or_package: RegistrationPayload | BankingReadinessPackage | dict[str, Any],
        action_type: Literal["registration", "banking"] = "registration",
        surface_id: str = "surface_hitl_approval",
    ) -> list[A2UITransportMessage]:
        """Construct interactive Human-in-the-Loop decision gate surface."""
        preview: dict[str, Any] = {}
        if isinstance(payload_or_package, RegistrationPayload):
            title = "Registration Payload Approval Gate"
            summary = (
                f"Verify official registration parameters for {payload_or_package.target_authority} "
                f"({payload_or_package.licence_category}) prior to formal submission."
            )
            preview = {
                "target_authority": payload_or_package.target_authority,
                "licence_category": payload_or_package.licence_category,
                "trade_name_candidates": payload_or_package.trade_name_candidates,
                "shareholding_structure": payload_or_package.shareholding_structure,
            }
        elif isinstance(payload_or_package, BankingReadinessPackage):
            title = "Corporate Banking Readiness Package Approval Gate"
            summary = (
                f"Review corporate banking dossier for partner {payload_or_package.bank_partner_id} "
                f"(Readiness Score: {payload_or_package.readiness_score}/100) before transmission."
            )
            preview = {
                "bank_partner_id": payload_or_package.bank_partner_id,
                "readiness_score": payload_or_package.readiness_score,
                "kyc_items_count": len(payload_or_package.kyc_kyb_checklist),
                "financial_projection_summary": "12-month projected P&L and source-of-funds narrative ready.",
            }
        elif isinstance(payload_or_package, dict):
            title = f"{action_type.capitalize()} Payload Approval Gate"
            summary = "Please review the prepared action payload before external transmission."
            preview = payload_or_package
        else:
            title = "Human-in-the-Loop Verification Gate"
            summary = "Action pending user authorization."

        components: list[dict[str, Any]] = [
            {
                "id": "approval_root",
                "component": "Column",
                "children": ["gate_card", "approval_actions_row"],
                "justify": "start",
                "align": "stretch",
            },
            {
                "id": "gate_card",
                "component": "ApprovalGateCard",
                "title": title,
                "summary": summary,
                "payload_preview": preview,
                "approve_action": {
                    "event": "hitl_approve",
                    "action_type": action_type,
                    "surface_id": surface_id,
                },
                "reject_action": {
                    "event": "hitl_reject",
                    "action_type": action_type,
                    "surface_id": surface_id,
                },
                "status": "pending",
            },
            {
                "id": "approval_actions_row",
                "component": "Row",
                "children": ["btn_approve", "btn_reject"],
                "justify": "end",
                "align": "center",
            },
            {
                "id": "btn_approve",
                "component": "Button",
                "label": "Approve & Submit",
                "action": {
                    "event": "hitl_approve",
                    "action_type": action_type,
                    "surface_id": surface_id,
                },
                "variant": "primary",
            },
            {
                "id": "btn_reject",
                "component": "Button",
                "label": "Request Edits",
                "action": {
                    "event": "hitl_reject",
                    "action_type": action_type,
                    "surface_id": surface_id,
                },
                "variant": "danger",
            },
        ]

        return self._wrap_messages(surface_id, components)

    def build_business_plan_surface(
        self,
        business_plan_md: str,
        compliance_md: str,
        artifact_urls: dict[str, str] | None = None,
        surface_id: str = "surface_business_plan",
    ) -> list[A2UITransportMessage]:
        """Construct Business Plan and Compliance Checklist surface with download links."""
        urls = artifact_urls or {}
        bp_url = urls.get("business_plan", "/workspace/business_plan.md")
        comp_url = urls.get("compliance_checklist", "/workspace/compliance_checklist.md")

        components: list[dict[str, Any]] = [
            {
                "id": "doc_root",
                "component": "Column",
                "children": ["doc_title", "card_business_plan", "card_compliance"],
                "justify": "start",
                "align": "stretch",
            },
            {
                "id": "doc_title",
                "component": "Text",
                "text": "Corporate Banking Documentation & Compliance Checklist",
                "variant": "title",
            },
            {
                "id": "card_business_plan",
                "component": "Card",
                "title": "Executive Business Plan & Financial Projections",
                "child": "viewer_business_plan",
                "variant": "elevated",
            },
            {
                "id": "viewer_business_plan",
                "component": "MarkdownViewer",
                "title": "Business Plan Document",
                "content": business_plan_md,
                "download_links": [
                    {
                        "filename": "business_plan.md",
                        "url": bp_url,
                    }
                ],
            },
            {
                "id": "card_compliance",
                "component": "Card",
                "title": "UAE Corporate Banking KYC/KYB Readiness Checklist",
                "child": "viewer_compliance",
                "variant": "elevated",
            },
            {
                "id": "viewer_compliance",
                "component": "MarkdownViewer",
                "title": "KYC/KYB Checklist",
                "content": compliance_md,
                "download_links": [
                    {
                        "filename": "compliance_checklist.md",
                        "url": comp_url,
                    }
                ],
            },
        ]

        return self._wrap_messages(surface_id, components)

    def build_regulatory_alert_surface(
        self,
        alerts: list[RegulatoryAlert],
        surface_id: str = "surface_regulatory_alerts",
    ) -> list[A2UITransportMessage]:
        """Construct A2UI Alert Banner surface displaying active regulatory changes."""
        root_children = ["alert_title"]
        alert_components: list[dict[str, Any]] = []

        for idx, alert in enumerate(alerts):
            card_id = f"card_alert_{idx}"
            col_id = f"col_alert_{idx}"
            badge_id = f"badge_alert_{idx}"
            text_id = f"text_alert_{idx}"
            source_id = f"source_alert_{idx}"

            root_children.append(card_id)
            alert_components.extend(
                [
                    {
                        "id": card_id,
                        "component": "Card",
                        "title": f"Regulatory Notice: {alert.authority}",
                        "child": col_id,
                        "variant": "elevated",
                    },
                    {
                        "id": col_id,
                        "component": "Column",
                        "children": [badge_id, text_id, source_id],
                        "justify": "start",
                        "align": "stretch",
                    },
                    {
                        "id": badge_id,
                        "component": "Badge",
                        "text": f"Effective: {alert.effective_date}",
                        "variant": "warning",
                    },
                    {
                        "id": text_id,
                        "component": "Text",
                        "text": alert.change_summary,
                        "variant": "body",
                    },
                    {
                        "id": source_id,
                        "component": "MarkdownViewer",
                        "title": "Official Regulatory Reference",
                        "content": f"Verified change source: [{alert.source_url}]({alert.source_url})",
                        "source_links": [
                            {"title": alert.authority, "url": alert.source_url}
                        ],
                    },
                ]
            )

        components: list[dict[str, Any]] = [
            {
                "id": "alert_root",
                "component": "Column",
                "children": root_children,
                "justify": "start",
                "align": "stretch",
            },
            {
                "id": "alert_title",
                "component": "Text",
                "text": "Active UAE Regulatory & Compliance Alerts",
                "variant": "title",
            },
            *alert_components,
        ]

        return self._wrap_messages(surface_id, components)

    @staticmethod
    def to_wire_dicts(messages: list[A2UITransportMessage]) -> list[dict[str, Any]]:
        """Serialize A2UI message models to wire transport dictionaries."""
        return [
            msg.model_dump(by_alias=True, exclude_none=True)
            if isinstance(msg, BaseModel)
            else msg
            for msg in messages
        ]
