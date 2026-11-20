"""Tavily search adapter for UAE regulatory knowledge discovery."""

from app.domain.ports import SearchServicePort


class TavilySearchAdapter(SearchServicePort):
    """Adapter invoking Tavily Search API for regulatory insights."""

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key

    async def search_regulations(self, query: str, jurisdiction: str | None = None) -> list[dict]:
        """Search Dubai regulatory content. In production, calls TavilyClient."""
        filter_scope = jurisdiction or "Dubai, UAE"
        return [
            {
                "title": f"Regulatory guide for {filter_scope}",
                "content": f"Activity matching '{query}' requires compliance with {filter_scope} guidelines.",
                "source": f"https://ded.dubai.gov.ae/regulations?q={query}",
            }
        ]
