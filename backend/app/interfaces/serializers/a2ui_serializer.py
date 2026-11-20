"""Serializers converting domain/workflow objects to A2UI component schemas."""

from typing import Any


class A2UIMessageSerializer:
    """Serializes application events into A2UI compatible surface payloads."""

    @staticmethod
    def create_card_surface(
        surface_id: str,
        title: str,
        description: str,
        badges: list[str] | None = None,
        actions: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Constructs an A2UI compliant Card component schema."""
        return {
            "version": "1.0",
            "type": "surface",
            "surface_id": surface_id,
            "root": {
                "type": "Card",
                "props": {
                    "title": title,
                    "description": description,
                    "badges": badges or [],
                    "actions": actions or [],
                },
            },
        }

    @staticmethod
    def create_progress_surface(
        surface_id: str,
        current_step: str,
        progress_percentage: int,
        log_message: str,
    ) -> dict[str, Any]:
        """Constructs an A2UI Progress indicator component schema."""
        return {
            "version": "1.0",
            "type": "surface",
            "surface_id": surface_id,
            "root": {
                "type": "ProgressTracker",
                "props": {
                    "currentStep": current_step,
                    "progress": progress_percentage,
                    "statusText": log_message,
                },
            },
        }
