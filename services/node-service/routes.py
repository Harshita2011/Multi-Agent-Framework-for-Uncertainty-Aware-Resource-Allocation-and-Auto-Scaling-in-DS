"""HTTP routes for the node service."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from simulator import NodeMetrics, NodeSimulator


class MetricsResponse(BaseModel):
    """Response model for the Phase 1 node metrics endpoint."""

    node_id: str
    cpu: float
    memory: float
    timestamp: int


def create_router(simulator: NodeSimulator) -> APIRouter:
    """Build the API router around the provided simulator instance.

    Passing the dependency in keeps request handling separate from simulation
    logic, which makes the code easier to extend in later phases.
    """

    router = APIRouter()

    @router.get("/metrics", response_model=MetricsResponse)
    def get_metrics() -> MetricsResponse:
        metrics: NodeMetrics = simulator.get_metrics()
        return MetricsResponse(
            node_id=metrics.node_id,
            cpu=metrics.cpu,
            memory=metrics.memory,
            timestamp=metrics.timestamp,
        )

    return router

