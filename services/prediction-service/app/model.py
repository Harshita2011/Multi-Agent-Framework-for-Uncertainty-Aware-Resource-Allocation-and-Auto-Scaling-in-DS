"""A lightweight GRU-style model for trend-aware sequence forecasting."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class SequenceFeatures:
    """Feature bundle extracted from a numeric history window."""

    level: float
    momentum: float
    volatility: float
    hidden_state: float


class LightweightGRUModel:
    """A tiny recurrent model that approximates GRU behavior without heavy ML deps.

    The model maintains a single hidden state and uses update/reset-style gates to
    blend the latest signal with recent context. It is intentionally simple so the
    service stays fast and easy to run in early phases.
    """

    def extract_features(self, history: Iterable[float]) -> SequenceFeatures:
        """Convert a history window into recurrent features for prediction."""

        values = [float(value) for value in history]
        if not values:
            raise ValueError("history must contain at least one value")

        hidden_state = values[0]
        previous = values[0]
        deltas: list[float] = []

        for value in values[1:]:
            delta = value - previous
            deltas.append(delta)

            update_gate = self._sigmoid(1.4 * delta)
            reset_gate = self._sigmoid(-0.8 * delta)
            candidate = math.tanh((reset_gate * hidden_state) + value)
            hidden_state = (1.0 - update_gate) * hidden_state + update_gate * candidate
            previous = value

        momentum = sum(deltas) / len(deltas) if deltas else 0.0
        mean_value = sum(values) / len(values)
        variance = sum((value - mean_value) ** 2 for value in values) / len(values)
        volatility = math.sqrt(variance)

        return SequenceFeatures(
            level=values[-1],
            momentum=momentum,
            volatility=volatility,
            hidden_state=hidden_state,
        )

    def predict_next(self, history: Iterable[float]) -> tuple[float, float]:
        """Forecast the next value plus an uncertainty estimate."""

        features = self.extract_features(history)
        recurrent_trend = (features.hidden_state - features.level) * 0.35
        prediction = features.level + features.momentum + recurrent_trend
        prediction = self._clamp(prediction)

        uncertainty = 0.03 + (features.volatility * 0.6) + abs(features.momentum) * 0.25
        uncertainty = min(round(uncertainty, 2), 0.5)

        return round(prediction, 2), uncertainty

    @staticmethod
    def _sigmoid(value: float) -> float:
        return 1.0 / (1.0 + math.exp(-value))

    @staticmethod
    def _clamp(value: float) -> float:
        return max(0.0, min(1.0, value))
