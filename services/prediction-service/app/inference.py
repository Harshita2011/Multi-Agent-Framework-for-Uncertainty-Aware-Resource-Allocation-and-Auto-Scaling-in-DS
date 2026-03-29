"""Inference orchestration for the prediction service."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from .model import LightweightGRUModel


@dataclass(frozen=True)
class PredictionResult:
    """Externally visible prediction output."""

    prediction: float
    uncertainty: float


class PredictionEngine:
    """Validates input history and delegates forecasting to the model."""

    def __init__(self, model: LightweightGRUModel) -> None:
        self._model = model

    def predict(self, history: Sequence[float]) -> PredictionResult:
        """Generate a trend-aware prediction with uncertainty."""

        if len(history) < 3:
            raise ValueError("history must include at least 3 values")

        normalized_history = [self._normalize(value) for value in history]
        prediction, uncertainty = self._model.predict_next(normalized_history)
        return PredictionResult(prediction=prediction, uncertainty=uncertainty)

    @staticmethod
    def _normalize(value: float) -> float:
        numeric_value = float(value)
        return max(0.0, min(1.0, numeric_value))
