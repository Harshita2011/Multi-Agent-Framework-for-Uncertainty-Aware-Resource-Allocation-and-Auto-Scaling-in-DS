"""HTTP routes for the node service."""

from __future__ import annotations

from fastapi import APIRouter, Response
from pydantic import BaseModel

from .metrics import NodeMetricsExporter
from .simulator import NodeMetrics, NodeSimulator


class MetricsResponse(BaseModel):
    """Response model for the Phase 1 node metrics endpoint."""

    node_id: str
    cpu: float
    memory: float
    timestamp: int


def create_router(simulator: NodeSimulator, metrics_exporter: NodeMetricsExporter) -> APIRouter:
    """Build the API router around the provided simulator and exporter."""

    router = APIRouter()

    @router.get("/metrics", response_model=MetricsResponse)
    def get_metrics() -> MetricsResponse:
        metrics: NodeMetrics = simulator.get_metrics()
        metrics_exporter.update(metrics)
        return MetricsResponse(
            node_id=metrics.node_id,
            cpu=metrics.cpu,
            memory=metrics.memory,
            timestamp=metrics.timestamp,
        )

    @router.get("/metrics/prometheus")
    def get_prometheus_metrics() -> Response:
        """Expose node metrics in Prometheus' text-based scrape format."""

        metrics = simulator.get_metrics()
        metrics_exporter.update(metrics)
        return Response(
            content=metrics_exporter.render(),
            media_type=metrics_exporter.content_type,
        )

    return router
