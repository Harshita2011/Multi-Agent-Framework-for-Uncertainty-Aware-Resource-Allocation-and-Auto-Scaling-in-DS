"""FastAPI entrypoint for the risk service."""

from __future__ import annotations

from fastapi import FastAPI

from .engine import RiskEngine
from .routes import create_router


def create_app() -> FastAPI:
    """Create the Phase 4 risk service application."""

    engine = RiskEngine()

    app = FastAPI(title="risk-service")
    app.include_router(create_router(engine=engine))
    return app


app = create_app()
