"""FastAPI routes for the coordinator service."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from .engine import CoordinatorEngine, DecisionInputs


class DecideRequest(BaseModel):
    """Decision request payload."""

    prediction: float
    risk: float


class DecideResponse(BaseModel):
    """Decision response payload."""

    action: str


def create_router(engine: CoordinatorEngine) -> APIRouter:
    """Expose the coordinator decision API."""

    router = APIRouter()

    @router.post("/decide", response_model=DecideResponse)
    def decide(request: DecideRequest) -> DecideResponse:
        inputs = DecisionInputs(
            prediction=_normalize(request.prediction),
            risk=_normalize(request.risk),
        )
        return DecideResponse(action=engine.decide(inputs))

    return router


def _normalize(value: float) -> float:
    numeric_value = float(value)
    return max(0.0, min(1.0, numeric_value))
