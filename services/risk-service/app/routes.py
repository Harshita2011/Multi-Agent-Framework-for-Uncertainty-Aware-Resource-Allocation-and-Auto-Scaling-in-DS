"""FastAPI routes for the risk service."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from .engine import RiskEngine, RiskInputs


class RiskRequest(BaseModel):
    """Risk scoring request payload."""

    cpu: float
    memory: float
    uncertainty: float


class RiskResponse(BaseModel):
    """Risk scoring response payload."""

    risk_score: float


def create_router(engine: RiskEngine) -> APIRouter:
    """Expose the risk scoring API around the provided engine."""

    router = APIRouter()

    @router.post("/risk", response_model=RiskResponse)
    def compute_risk(request: RiskRequest) -> RiskResponse:
        inputs = RiskInputs(
            cpu=_normalize(request.cpu),
            memory=_normalize(request.memory),
            uncertainty=_normalize(request.uncertainty),
        )
        return RiskResponse(risk_score=engine.score(inputs))

    return router


def _normalize(value: float) -> float:
    """Keep incoming signals inside the normalized range expected by the API."""

    numeric_value = float(value)
    return max(0.0, min(1.0, numeric_value))
