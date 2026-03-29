"""FastAPI entrypoint for the node service."""

from __future__ import annotations

import os

from fastapi import FastAPI

from .metrics import NodeMetricsExporter
from .routes import create_router
from .simulator import NodeSimulator


def create_app() -> FastAPI:
    """Create the node service application."""

    node_id = os.getenv("NODE_ID", "node-1")
    simulator = NodeSimulator(node_id=node_id)
    metrics_exporter = NodeMetricsExporter()

    app = FastAPI(title="node-service")
    app.include_router(create_router(simulator=simulator, metrics_exporter=metrics_exporter))
    return app


app = create_app()
