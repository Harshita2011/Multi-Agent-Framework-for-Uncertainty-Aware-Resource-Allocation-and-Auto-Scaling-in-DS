"""FastAPI entrypoint for the allocation service."""

from __future__ import annotations

from fastapi import FastAPI

from .planner import GreedyAllocator
from .routes import create_router


def create_app() -> FastAPI:
    """Create the Phase 7 allocation service application."""

    allocator = GreedyAllocator()

    app = FastAPI(title="allocation-service")
    app.include_router(create_router(allocator=allocator))
    return app


app = create_app()
