"""Prometheus metrics helpers for the node service."""

from __future__ import annotations

from prometheus_client import CONTENT_TYPE_LATEST, CollectorRegistry, Gauge, generate_latest

from .simulator import NodeMetrics


class NodeMetricsExporter:
    """Maintains scrapeable Prometheus gauges for simulated node metrics.

    Keeping monitoring state in a dedicated helper avoids mixing Prometheus
    concerns directly into the simulation code.
    """

    def __init__(self) -> None:
        self._registry = CollectorRegistry()
        self._cpu_gauge = Gauge(
            "cpu_usage",
            "Current simulated CPU usage for a node.",
            labelnames=("node_id",),
            registry=self._registry,
        )
        self._memory_gauge = Gauge(
            "memory_usage",
            "Current simulated memory usage for a node.",
            labelnames=("node_id",),
            registry=self._registry,
        )
        self._timestamp_gauge = Gauge(
            "node_metrics_timestamp",
            "Unix timestamp of the latest simulated metrics sample.",
            labelnames=("node_id",),
            registry=self._registry,
        )

    @property
    def content_type(self) -> str:
        """Return the Prometheus text format content type."""

        return CONTENT_TYPE_LATEST

    def update(self, metrics: NodeMetrics) -> None:
        """Push the latest node metrics into the Prometheus registry."""

        labels = {"node_id": metrics.node_id}
        self._cpu_gauge.labels(**labels).set(metrics.cpu)
        self._memory_gauge.labels(**labels).set(metrics.memory)
        self._timestamp_gauge.labels(**labels).set(metrics.timestamp)

    def render(self) -> bytes:
        """Render the current registry in Prometheus text format."""

        return generate_latest(self._registry)
