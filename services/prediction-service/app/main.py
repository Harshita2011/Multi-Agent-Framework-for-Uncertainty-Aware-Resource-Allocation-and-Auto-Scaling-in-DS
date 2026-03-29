"""FastAPI entrypoint for the prediction service."""

from __future__ import annotations

from fastapi import FastAPI

from .inference import PredictionEngine
from .model import LightweightGRUModel
from .routes import create_router


def create_app() -> FastAPI:
    """Create the Phase 3 prediction service application."""

    model = LightweightGRUModel()
    engine = PredictionEngine(model=model)

    app = FastAPI(title="prediction-service")
    app.include_router(create_router(engine=engine))
    return app


app = create_app()
