"""FastAPI entrypoint for the coordinator service."""

from __future__ import annotations

from fastapi import FastAPI

from .engine import CoordinatorEngine
from .routes import create_router


def create_app() -> FastAPI:
    """Create the Phase 8 coordinator service application."""

    engine = CoordinatorEngine()

    app = FastAPI(title="coordinator-service")
    app.include_router(create_router(engine=engine))
    return app


app = create_app()
