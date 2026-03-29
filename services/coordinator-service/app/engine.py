"""Central decision logic for scaling coordination."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DecisionInputs:
    """Normalized inputs used by the coordinator."""

    prediction: float
    risk: float


class CoordinatorEngine:
    """Combines prediction and risk into a simple scaling action."""

    def decide(self, inputs: DecisionInputs) -> str:
        """Return a logical action for the current operating state."""

        if inputs.prediction >= 0.7 and inputs.risk >= 0.5:
            return "scale_up"
        if inputs.prediction <= 0.35 and inputs.risk <= 0.4:
            return "scale_down"
        return "hold"
