"""FastAPI routes for the evaluation service."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from .engine import EvaluationEngine, MetricsSnapshot


class MetricsResponse(BaseModel):
    """Evaluation metrics response payload."""

    rmse: float
    utilization: float


class ObservationRequest(BaseModel):
    """Observation payload for updating evaluation metrics."""

    prediction: float
    actual: float
    utilization: float


def create_router(engine: EvaluationEngine) -> APIRouter:
    """Expose evaluation metrics endpoints."""

    router = APIRouter()

    @router.get("/metrics", response_model=MetricsResponse)
    def get_metrics() -> MetricsResponse:
        return _to_response(engine.snapshot())

    @router.post("/metrics/observations", response_model=MetricsResponse)
    def add_observation(request: ObservationRequest) -> MetricsResponse:
        snapshot = engine.record(
            prediction=request.prediction,
            actual=request.actual,
            utilization=request.utilization,
        )
        return _to_response(snapshot)

    return router


def _to_response(snapshot: MetricsSnapshot) -> MetricsResponse:
    return MetricsResponse(
        rmse=snapshot.rmse,
        utilization=snapshot.utilization,
    )
