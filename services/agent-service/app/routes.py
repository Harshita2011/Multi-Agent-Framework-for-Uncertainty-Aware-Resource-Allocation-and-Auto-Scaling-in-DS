"""FastAPI routes for the agent service."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from .agents import EvaluationInputs, cost_agent, performance_agent, risk_agent


class EvaluateRequest(BaseModel):
    """Evaluation request payload."""

    cpu: float
    risk: float


class EvaluateResponse(BaseModel):
    """Evaluation response payload."""

    performance_score: float
    cost_score: float
    risk_score: float


def create_router() -> APIRouter:
    """Expose the multi-agent evaluation API."""

    router = APIRouter()

    @router.post("/evaluate", response_model=EvaluateResponse)
    def evaluate(request: EvaluateRequest) -> EvaluateResponse:
        inputs = EvaluationInputs(
            cpu=_normalize(request.cpu),
            risk=_normalize(request.risk),
        )
        return EvaluateResponse(
            performance_score=performance_agent(inputs),
            cost_score=cost_agent(inputs),
            risk_score=risk_agent(inputs),
        )

    return router


def _normalize(value: float) -> float:
    """Keep incoming values in the normalized range expected by the API."""

    numeric_value = float(value)
    return max(0.0, min(1.0, numeric_value))
