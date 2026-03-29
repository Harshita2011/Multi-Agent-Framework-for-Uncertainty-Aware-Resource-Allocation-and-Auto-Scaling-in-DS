"""FastAPI routes for the prediction service."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from .inference import PredictionEngine, PredictionResult


class PredictRequest(BaseModel):
    """Prediction request payload."""

    history: list[float] = Field(..., min_length=3)


class PredictResponse(BaseModel):
    """Prediction response payload."""

    prediction: float
    uncertainty: float


def create_router(engine: PredictionEngine) -> APIRouter:
    """Expose the prediction API around the provided inference engine."""

    router = APIRouter()

    @router.post("/predict", response_model=PredictResponse)
    def predict(request: PredictRequest) -> PredictResponse:
        try:
            result: PredictionResult = engine.predict(request.history)
        except ValueError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error

        return PredictResponse(
            prediction=result.prediction,
            uncertainty=result.uncertainty,
        )

    return router
