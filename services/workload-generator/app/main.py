"""FastAPI entrypoint for the workload generator service."""

from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel

from .generator import WorkloadGenerator


class LoadResponse(BaseModel):
    """Response model for the Phase 1 workload endpoint."""

    load: float


def create_app() -> FastAPI:
    """Create the Phase 1 workload generator application."""

    generator = WorkloadGenerator()
    app = FastAPI(title="workload-generator")

    @app.get("/load", response_model=LoadResponse)
    def get_load() -> LoadResponse:
        return LoadResponse(load=generator.get_load())

    return app


app = create_app()

