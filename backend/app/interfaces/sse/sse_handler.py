"""Server-Sent Events (SSE) formatting utilities."""

import json
from typing import Any


def format_sse_message(event: str, data: dict[str, Any] | str) -> str:
    """Formats an event and payload according to the SSE standard specification."""
    data_str = json.dumps(data) if isinstance(data, dict) else str(data)
    return f"event: {event}\ndata: {data_str}\n\n"
