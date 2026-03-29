"""In-memory resource pool management."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ResourceSnapshot:
    """Serializable view of the current node pool."""

    small: int
    medium: int
    large: int


class ResourceManager:
    """Tracks the available node pool in memory."""

    def __init__(self) -> None:
        self._resources = {
            "small": 5,
            "medium": 3,
            "large": 2,
        }

    def snapshot(self) -> ResourceSnapshot:
        """Return the current resource counts."""

        return ResourceSnapshot(
            small=self._resources["small"],
            medium=self._resources["medium"],
            large=self._resources["large"],
        )

    def allocate(self, node_type: str, count: int = 1) -> ResourceSnapshot:
        """Reduce the available count for the requested node type."""

        self._validate_request(node_type=node_type, count=count)
        self._resources[node_type] = max(0, self._resources[node_type] - count)
        return self.snapshot()

    def release(self, node_type: str, count: int = 1) -> ResourceSnapshot:
        """Increase the available count for the requested node type."""

        self._validate_request(node_type=node_type, count=count)
        self._resources[node_type] += count
        return self.snapshot()

    def _validate_request(self, node_type: str, count: int) -> None:
        if node_type not in self._resources:
            raise ValueError("node_type must be one of: small, medium, large")
        if count < 1:
            raise ValueError("count must be at least 1")
