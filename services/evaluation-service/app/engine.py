"""Evaluation metrics for prediction accuracy and utilization."""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class MetricsSnapshot:
    """Serializable view of the current evaluation metrics."""

    rmse: float
    utilization: float


class EvaluationEngine:
    """Tracks simple in-memory observations and computes evaluation metrics."""

    def __init__(self) -> None:
        self._predictions = [0.70, 0.62, 0.81]
        self._actuals = [0.72, 0.60, 0.78]
        self._utilizations = [0.75, 0.80, 0.79]

    def snapshot(self) -> MetricsSnapshot:
        """Return the latest RMSE and average utilization."""

        rmse = self._compute_rmse(self._predictions, self._actuals)
        utilization = sum(self._utilizations) / len(self._utilizations)
        return MetricsSnapshot(
            rmse=round(rmse, 2),
            utilization=round(utilization, 2),
        )

    def record(self, prediction: float, actual: float, utilization: float) -> MetricsSnapshot:
        """Append a new evaluation sample and return updated metrics."""

        self._predictions.append(self._normalize(prediction))
        self._actuals.append(self._normalize(actual))
        self._utilizations.append(self._normalize(utilization))
        return self.snapshot()

    @staticmethod
    def _compute_rmse(predictions: list[float], actuals: list[float]) -> float:
        squared_error = sum((prediction - actual) ** 2 for prediction, actual in zip(predictions, actuals))
        mean_squared_error = squared_error / len(predictions)
        return math.sqrt(mean_squared_error)

    @staticmethod
    def _normalize(value: float) -> float:
        numeric_value = float(value)
        return max(0.0, min(1.0, numeric_value))
