"""FastAPI entrypoint for the agent service."""

from __future__ import annotations

from fastapi import FastAPI

from .routes import create_router


def create_app() -> FastAPI:
    """Create the Phase 5 agent service application."""

    app = FastAPI(title="agent-service")
    app.include_router(create_router())
    return app


app = create_app()
