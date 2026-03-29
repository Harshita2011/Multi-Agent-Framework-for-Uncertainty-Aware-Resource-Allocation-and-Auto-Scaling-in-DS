"""Simple multi-agent scoring functions."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EvaluationInputs:
    """Normalized signals used by the scoring agents."""

    cpu: float
    risk: float


def performance_agent(inputs: EvaluationInputs) -> float:
    """Score how strongly the node appears to meet demand.

    Higher CPU implies the node is actively carrying work, so the performance
    score trends upward with utilization while a high risk score trims it.
    """

    score = (inputs.cpu * 0.85) + ((1.0 - inputs.risk) * 0.15)
    return round(_clamp(score), 2)


def cost_agent(inputs: EvaluationInputs) -> float:
    """Score cost efficiency.

    Lower CPU and lower risk suggest lower operating pressure, which maps to a
    better cost score in this phase's lightweight heuristic.
    """

    score = ((1.0 - inputs.cpu) * 0.70) + ((1.0 - inputs.risk) * 0.30)
    return round(_clamp(score), 2)


def risk_agent(inputs: EvaluationInputs) -> float:
    """Pass through the normalized risk signal as the agent's risk score."""

    return round(_clamp(inputs.risk), 2)


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, value))
