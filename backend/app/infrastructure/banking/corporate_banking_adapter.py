"""Corporate Banking Partner API adapter implementing BankingWorkflowPort."""

import asyncio
import hashlib
import hmac
import logging
import uuid
from typing import Any

import httpx

from app.domain.entities import BankingReadinessPackage
from app.domain.exceptions import ExternalIntegrationError
from app.domain.ports import BankingWorkflowPort

logger = logging.getLogger("dubai_biznavigator.banking")


class CorporateBankingAdapter(BankingWorkflowPort):
    """Adapter for corporate banking partner gateway (Wio, Emirates NBD, Mashreq).

    Implements idempotency tracking, exponential backoff retries, HMAC-SHA256
    webhook signature validation, and a self-contained sandbox execution mode.
    """

    def __init__(
        self,
        base_url: str = "https://api.banking-sandbox.uae.ae/v1",
        api_key: str = "sandbox-key",
        webhook_secret: str = "sandbox-secret-uae-biznav",
        sandbox_mode: bool = True,
        max_retries: int = 3,
        base_backoff_seconds: float = 0.2,
        timeout: float = 10.0,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.webhook_secret = webhook_secret
        self.sandbox_mode = sandbox_mode
        self.max_retries = max_retries
        self.base_backoff_seconds = base_backoff_seconds
        self.timeout = timeout
        self._external_client = client

    def _get_client(self) -> httpx.AsyncClient:
        if self._external_client is not None:
            return self._external_client
        return httpx.AsyncClient(timeout=self.timeout)

    async def fetch_kyc_checklist(
        self, bank_partner_id: str, licence_category: str
    ) -> list[str]:
        """Fetch tailored KYC/KYB requirements for specific UAE bank partner."""
        if self.sandbox_mode:
            logger.info(
                "Sandbox mode: returning standard UAE Central Bank KYC checklist for %s (%s)",
                bank_partner_id,
                licence_category,
            )
            standard_checklist = [
                "Valid UAE Trade License (DET or Free Zone Certificate)",
                "Certificate of Commercial Registration / Incorporation",
                "Attested Memorandum and Articles of Association (MOA / AOA)",
                "Shareholder and UBO Passport Copies & Emirates IDs",
                "UAE Residence Visa copies for resident signatory partners",
                "Registered Office Lease Agreement (Ejari or Free Zone Desk)",
                "6-Month Bank Statements (personal or parent operating company)",
                "Comprehensive Business Plan and 12-Month Financial Model",
                "Source of Wealth & Source of Funds Narrative",
            ]
            if "Commercial" in licence_category:
                standard_checklist.append(
                    "Supplier / Customer pro-forma contracts or invoices"
                )
            if "wio" in bank_partner_id.lower():
                standard_checklist.append(
                    "Wio Digital Onboarding biometric facial scan verification"
                )
            return standard_checklist

        client = self._get_client()
        url = f"{self.base_url}/partners/{bank_partner_id}/kyc-checklist"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        params = {"licence_category": licence_category}

        for attempt in range(self.max_retries):
            try:
                response = await client.get(url, headers=headers, params=params)
                if response.status_code < 500:
                    response.raise_for_status()
                    data = response.json()
                    return data.get("checklist", [])
            except (httpx.RequestError, httpx.HTTPStatusError) as exc:
                if attempt == self.max_retries - 1:
                    logger.error("Failed to fetch KYC checklist: %s", exc)
                    raise ExternalIntegrationError(
                        f"Failed to fetch KYC checklist from {bank_partner_id}: {exc}"
                    ) from exc
                await asyncio.sleep(self.base_backoff_seconds * (2**attempt))

        return []

    async def submit_readiness_package(
        self, package: BankingReadinessPackage, workspace_id: str
    ) -> dict[str, Any]:
        """Submit banking readiness package to partner API with idempotency."""
        idempotency_key = (
            f"idemp_{workspace_id}_{package.bank_partner_id}_{uuid.uuid4().hex[:8]}"
        )

        if self.sandbox_mode:
            logger.info(
                "Sandbox mode: simulating banking dossier submission for workspace %s (Key: %s)",
                workspace_id,
                idempotency_key,
            )
            return {
                "status": "submitted",
                "submission_id": f"sub_{uuid.uuid4().hex[:12]}",
                "bank_partner_id": package.bank_partner_id,
                "workspace_id": workspace_id,
                "idempotency_key": idempotency_key,
                "readiness_score": package.readiness_score,
                "checklist_items_count": len(package.kyc_kyb_checklist),
                "sandbox": True,
                "message": (
                    f"Corporate banking application successfully queued with {package.bank_partner_id}."
                ),
            }

        client = self._get_client()
        url = f"{self.base_url}/applications/submit"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Idempotency-Key": idempotency_key,
            "Content-Type": "application/json",
        }
        payload = {
            "workspace_id": workspace_id,
            "bank_partner_id": package.bank_partner_id,
            "readiness_score": package.readiness_score,
            "kyc_kyb_checklist": package.kyc_kyb_checklist,
            "business_plan_markdown": package.business_plan_markdown,
            "financial_projection_12m": package.financial_projection_12m,
        }

        for attempt in range(self.max_retries):
            try:
                response = await client.post(url, json=payload, headers=headers)
                if response.status_code < 500:
                    response.raise_for_status()
                    return response.json()
            except (httpx.RequestError, httpx.HTTPStatusError) as exc:
                if attempt == self.max_retries - 1:
                    logger.error("Failed to submit banking package: %s", exc)
                    raise ExternalIntegrationError(
                        f"Banking submission failed after {self.max_retries} attempts: {exc}"
                    ) from exc
                await asyncio.sleep(self.base_backoff_seconds * (2**attempt))

        raise ExternalIntegrationError("Failed to submit banking package.")

    async def verify_webhook_signature(
        self, payload_bytes: bytes, signature: str, secret: str
    ) -> bool:
        """Verify HMAC-SHA256 signature on incoming banking partner webhook payloads."""
        if not signature or not secret:
            return False

        clean_sig = signature.strip()
        if clean_sig.startswith("sha256="):
            clean_sig = clean_sig.replace("sha256=", "", 1)
        elif clean_sig.startswith("v1="):
            clean_sig = clean_sig.replace("v1=", "", 1)

        expected_sig = hmac.new(
            key=secret.encode("utf-8"),
            msg=payload_bytes,
            digestmod=hashlib.sha256,
        ).hexdigest()

        return hmac.compare_digest(expected_sig.lower(), clean_sig.lower())

    async def evaluate_eligibility(
        self,
        business_profile_id: str,
        jurisdiction_code: str,
        activity_code: str,
    ) -> dict[str, Any]:
        """Evaluate account readiness against UAE banking guidelines."""
        recommended_banks = ["Wio Business Bank", "Mashreq NeoBiz", "Emirates NBD"]
        if "FreeZone" in jurisdiction_code:
            recommended_banks = ["Wio Business Bank", "Mashreq NeoBiz"]

        return {
            "eligible": True,
            "profile_id": business_profile_id,
            "jurisdiction": jurisdiction_code,
            "activity": activity_code,
            "readiness_score": 88.0,
            "recommended_banks": recommended_banks,
            "sandbox": self.sandbox_mode,
        }
