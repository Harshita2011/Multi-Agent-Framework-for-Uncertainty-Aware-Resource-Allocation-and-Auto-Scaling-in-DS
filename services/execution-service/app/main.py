"""FastAPI entrypoint for the execution service."""

from __future__ import annotations

from fastapi import FastAPI

from .executor import ExecutionEngine
from .routes import create_router


def create_app() -> FastAPI:
    """Create the Phase 9 execution service application."""

    engine = ExecutionEngine()

    app = FastAPI(title="execution-service")
    app.include_router(create_router(engine=engine))
    return app


app = create_app()
