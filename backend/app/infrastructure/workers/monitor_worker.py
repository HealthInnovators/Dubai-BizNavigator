"""Worker executing scheduled regulatory change detection with Langfuse tracing and flush."""

import asyncio
import logging

from langfuse import observe, propagate_attributes

from app.application.regulatory_monitor import RegulatoryUpdateMonitor
from app.domain.entities import RegulatoryAlert
from app.domain.ports import ObservabilityPort

logger = logging.getLogger("dubai_biznavigator.monitor_worker")


class RegulatoryMonitorWorker:
    """Scheduled background worker running the RegulatoryUpdateMonitor under Langfuse observability."""

    def __init__(
        self,
        monitor: RegulatoryUpdateMonitor,
        observability: ObservabilityPort | None = None,
    ) -> None:
        self.monitor = monitor
        self.observability = observability

    @observe(name="regulatory-monitor-cycle")
    async def run_once(self) -> list[RegulatoryAlert]:
        """Execute a single regulatory monitoring cycle wrapped in Langfuse trace tags."""
        with propagate_attributes(tags=["regulatory-monitor"]):
            try:
                logger.info("Starting scheduled regulatory update monitoring cycle...")
                alerts = await self.monitor.check_for_updates()
                logger.info(
                    "Regulatory monitoring cycle finished. Generated %d alert(s).",
                    len(alerts),
                )
                return alerts
            except Exception as exc:
                logger.error("Error during regulatory monitor execution: %s", exc, exc_info=True)
                raise
            finally:
                if self.observability is not None:
                    logger.debug("Flushing Langfuse telemetry before worker exits.")
                    await self.observability.flush()

    async def run_continuous(
        self,
        interval_seconds: float = 3600.0,
        max_iterations: int | None = None,
    ) -> None:
        """Continuously run regulatory check on an interval for standing daemons."""
        iterations = 0
        while max_iterations is None or iterations < max_iterations:
            try:
                await self.run_once()
            except Exception as exc:
                logger.warning("Monitoring iteration %d failed: %s", iterations, exc)

            iterations += 1
            if max_iterations is not None and iterations >= max_iterations:
                break
            await asyncio.sleep(interval_seconds)
