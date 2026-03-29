"""Greedy resource allocation logic."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AllocationPlan:
    """Serializable greedy allocation result."""

    allocation: dict[str, int]


class GreedyAllocator:
    """Select node combinations with a largest-fitting-first heuristic.

    The planner prefers larger nodes first, but only when their capacity does
    not overshoot the remaining requirement. This keeps the output aligned with
    the phase example where `1.0` CPU maps to two `medium` nodes instead of a
    single oversized `large` node.
    """

    def __init__(self) -> None:
        self._node_capacities = {
            "large": 2.0,
            "medium": 0.5,
            "small": 0.25,
        }

    def allocate(self, cpu_required: float) -> AllocationPlan:
        """Return a greedy allocation for the requested CPU requirement."""

        remaining = round(float(cpu_required), 2)
        if remaining <= 0:
            raise ValueError("cpu_required must be greater than 0")

        allocation: dict[str, int] = {}

        for node_type, capacity in self._node_capacities.items():
            count = 0
            while remaining + 1e-9 >= capacity:
                remaining = round(remaining - capacity, 2)
                count += 1

            if count > 0:
                allocation[node_type] = count

        if remaining > 0:
            smallest_capacity = self._node_capacities["small"]
            extra_small = int(round(remaining / smallest_capacity))
            if extra_small > 0:
                allocation["small"] = allocation.get("small", 0) + extra_small

        return AllocationPlan(allocation=allocation)
