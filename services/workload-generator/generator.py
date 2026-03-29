"""Dynamic load generation for the workload service."""

from __future__ import annotations

import math
import random
import time


class WorkloadGenerator:
    """Produces a simple, changing load signal for downstream services.

    Phase 1 only needs a dynamic source of load, so this generator keeps a
    lightweight in-memory state instead of introducing queues or persistence.
    """

    def __init__(self) -> None:
        self._random = random.Random("workload-generator")
        self._load = 0.50
        self._phase = self._random.uniform(0.0, math.tau)
        self._last_updated_at = time.time()

    def get_load(self) -> float:
        """Advance the load pattern and return a normalized value."""

        now = time.time()
        elapsed_seconds = max(now - self._last_updated_at, 0.0)
        self._last_updated_at = now

        wave = 0.55 + 0.25 * math.sin(now / 5.0 + self._phase)
        noise = self._random.uniform(-0.04, 0.04)
        smoothing = min(max(elapsed_seconds, 0.2), 1.5) / 2.0

        self._load = self._clamp(self._load + (wave - self._load) * smoothing + noise)
        return round(self._load, 2)

    @staticmethod
    def _clamp(value: float) -> float:
        """Keep load values in the API's expected normalized range."""

        return max(0.0, min(1.0, value))
