"""Execution simulation for coordinator actions."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ExecutionResult:
    """Result of a simulated action."""

    status: str
    message: str


class ExecutionEngine:
    """Applies actions in memory and records a simple execution log."""

    def __init__(self) -> None:
        self._scaled_up_count = 0
        self._scaled_down_count = 0
        self._isolated_count = 0
        self._history: list[str] = []

    def execute(self, action: str) -> ExecutionResult:
        """Simulate the requested action and return a status result."""

        normalized_action = action.strip().lower()

        if normalized_action == "scale_up":
            self._scaled_up_count += 1
            return self._record("scale_up applied: increased simulated capacity")

        if normalized_action == "scale_down":
            self._scaled_down_count += 1
            return self._record("scale_down applied: reduced simulated capacity")

        if normalized_action == "isolate":
            self._isolated_count += 1
            return self._record("isolate applied: quarantined simulated node")

        if normalized_action == "hold":
            return self._record("hold applied: kept simulated system unchanged")

        raise ValueError("action must be one of: scale_up, scale_down, isolate, hold")

    def history(self) -> list[str]:
        """Return the in-memory execution history."""

        return list(self._history)

    def _record(self, message: str) -> ExecutionResult:
        self._history.append(message)
        return ExecutionResult(status="success", message=message)
