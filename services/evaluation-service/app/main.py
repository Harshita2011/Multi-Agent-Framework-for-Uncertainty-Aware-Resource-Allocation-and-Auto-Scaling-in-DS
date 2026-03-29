"""FastAPI entrypoint for the evaluation service."""

from __future__ import annotations

from fastapi import FastAPI

from .engine import EvaluationEngine
from .routes import create_router


def create_app() -> FastAPI:
    """Create the Phase 10 evaluation service application."""

    engine = EvaluationEngine()

    app = FastAPI(title="evaluation-service")
    app.include_router(create_router(engine=engine))
    return app


app = create_app()
