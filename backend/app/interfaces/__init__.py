"""Interfaces layer - HTTP routers, SSE handlers, A2UI serializers, and DI."""

from typing import Any

__all__ = ["Container", "get_container"]


def __getattr__(name: str) -> Any:
    if name in ("Container", "get_container"):
        from app.interfaces.container import Container, get_container

        if name == "Container":
            return Container
        return get_container
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
