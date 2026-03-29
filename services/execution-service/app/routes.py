"""FastAPI routes for the execution service."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from .executor import ExecutionEngine, ExecutionResult


class ExecuteRequest(BaseModel):
    """Execution request payload."""

    action: str


class ExecuteResponse(BaseModel):
    """Execution response payload."""

    status: str


class HistoryResponse(BaseModel):
    """Execution history payload."""

    actions: list[str]


def create_router(engine: ExecutionEngine) -> APIRouter:
    """Expose the execution API around the provided engine."""

    router = APIRouter()

    @router.post("/execute", response_model=ExecuteResponse)
    def execute(request: ExecuteRequest) -> ExecuteResponse:
        try:
            result: ExecutionResult = engine.execute(request.action)
        except ValueError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error
        return ExecuteResponse(status=result.status)

    @router.get("/execution/history", response_model=HistoryResponse)
    def get_history() -> HistoryResponse:
        return HistoryResponse(actions=engine.history())

    return router
