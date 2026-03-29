"""Risk scoring logic for instability estimation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class RiskInputs:
    """Normalized values used to compute instability risk."""

    cpu: float
    memory: float
    uncertainty: float


class RiskEngine:
    """Computes an interpretable instability score from system signals.

    The score blends overall utilization, imbalance between resources, and
    prediction uncertainty so that heavily loaded or volatile nodes surface as
    higher risk.
    """

    def score(self, inputs: RiskInputs) -> float:
        """Return a bounded risk score in the normalized range [0, 1]."""

        values = [inputs.cpu, inputs.memory, inputs.uncertainty]
        utilization = (inputs.cpu + inputs.memory) / 2.0
        variance = self._variance(values)

        # Weight current pressure most, while still surfacing instability.
        risk_score = (
            utilization * 0.55
            + inputs.uncertainty * 0.25
            + variance * 1.2
            + abs(inputs.cpu - inputs.memory) * 0.10
        )
        return round(self._clamp(risk_score), 2)

    @staticmethod
    def _variance(values: Sequence[float]) -> float:
        mean_value = sum(values) / len(values)
        return sum((value - mean_value) ** 2 for value in values) / len(values)

    @staticmethod
    def _clamp(value: float) -> float:
        return max(0.0, min(1.0, value))
