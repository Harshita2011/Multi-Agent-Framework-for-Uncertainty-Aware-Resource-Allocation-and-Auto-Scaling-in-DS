"""FastAPI entrypoint for the resource service."""

from __future__ import annotations

from fastapi import FastAPI

from .manager import ResourceManager
from .routes import create_router


def create_app() -> FastAPI:
    """Create the Phase 6 resource service application."""

    manager = ResourceManager()

    app = FastAPI(title="resource-service")
    app.include_router(create_router(manager=manager))
    return app


app = create_app()
