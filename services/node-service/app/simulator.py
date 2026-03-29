"""Simulation logic for the node service."""

from __future__ import annotations

import math
import random
import time
from dataclasses import dataclass


@dataclass(frozen=True)
class NodeMetrics:
    """Represents the externally visible metrics for a simulated node."""

    node_id: str
    cpu: float
    memory: float
    timestamp: int


class NodeSimulator:
    """Produces lightweight CPU and memory values that drift over time.

    The simulator keeps state in memory because Phase 1 explicitly avoids
    persistence. A per-node random seed makes separate node instances evolve
    differently while still staying predictable enough for local development.
    """

    def __init__(self, node_id: str) -> None:
        self._node_id = node_id
        self._random = random.Random(node_id)
        self._cpu = self._random.uniform(0.35, 0.65)
        self._memory = self._random.uniform(0.40, 0.70)
        self._last_updated_at = time.time()
        self._phase = self._random.uniform(0.0, math.tau)

    def get_metrics(self) -> NodeMetrics:
        """Advance the simulation slightly and return the latest snapshot."""

        now = time.time()
        elapsed_seconds = max(now - self._last_updated_at, 0.0)
        self._last_updated_at = now

        self._advance(elapsed_seconds=elapsed_seconds, current_time=now)

        return NodeMetrics(
            node_id=self._node_id,
            cpu=round(self._cpu, 2),
            memory=round(self._memory, 2),
            timestamp=int(now),
        )

    def _advance(self, elapsed_seconds: float, current_time: float) -> None:
        """Move utilization using a smooth trend plus bounded random noise.

        The sinusoidal term gives a realistic gradual rise and fall, while the
        noise prevents the values from feeling too synthetic.
        """

        wave_position = current_time / 6.0 + self._phase
        cpu_target = 0.55 + 0.20 * math.sin(wave_position)
        memory_target = 0.58 + 0.16 * math.cos(wave_position / 1.3)

        smoothing = min(max(elapsed_seconds, 0.2), 1.5) / 2.0
        cpu_noise = self._random.uniform(-0.03, 0.03)
        memory_noise = self._random.uniform(-0.02, 0.02)

        self._cpu = self._clamp(self._cpu + (cpu_target - self._cpu) * smoothing + cpu_noise)

        # Memory follows its own target but is also nudged by CPU so the two
        # metrics feel related instead of behaving like independent dice rolls.
        memory_next = self._memory + (memory_target - self._memory) * smoothing
        memory_next += (self._cpu - self._memory) * 0.12 + memory_noise
        self._memory = self._clamp(memory_next)

    @staticmethod
    def _clamp(value: float) -> float:
        """Keep utilization inside the normalized API range."""

        return max(0.0, min(1.0, value))
