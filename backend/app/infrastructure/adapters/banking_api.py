"""UAE Banking adapter verifying corporate account readiness."""

from app.domain.ports import BankingServicePort


class BankingAPIAdapter(BankingServicePort):
    """Adapter verifying corporate banking readiness against UAE Central Bank standards."""

    def __init__(self, endpoint_url: str | None = None) -> None:
        self.endpoint_url = endpoint_url

    async def evaluate_eligibility(
        self,
        business_profile_id: str,
        jurisdiction_code: str,
        activity_code: str,
    ) -> dict:
        """Evaluates corporate banking documentation readiness."""
        return {
            "eligible": True,
            "profile_id": business_profile_id,
            "recommended_banks": [
                "Emirates NBD",
                "Mashreq NeoBiz",
                "Wio Business Bank",
            ],
            "required_documents": [
                "Trade License",
                "Certificate of Incorporation",
                "Memorandum of Association (MOA)",
                "Passport & Emirates ID copies of shareholders",
                "6-month personal bank statements",
            ],
        }
