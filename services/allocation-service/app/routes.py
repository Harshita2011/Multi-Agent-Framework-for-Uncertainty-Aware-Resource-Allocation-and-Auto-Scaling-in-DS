"""FastAPI routes for the allocation service."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from .planner import AllocationPlan, GreedyAllocator


class AllocateRequest(BaseModel):
    """Allocation request payload."""

    cpu_required: float


class AllocationPayload(BaseModel):
    """Allocated node counts by type."""

    large: int | None = None
    medium: int | None = None
    small: int | None = None


class AllocateResponse(BaseModel):
    """Allocation response payload."""

    allocation: AllocationPayload


def create_router(allocator: GreedyAllocator) -> APIRouter:
    """Expose the greedy allocation API."""

    router = APIRouter()

    @router.post("/allocate", response_model=AllocateResponse)
    def allocate(request: AllocateRequest) -> AllocateResponse:
        try:
            plan: AllocationPlan = allocator.allocate(request.cpu_required)
        except ValueError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error

        return AllocateResponse(allocation=AllocationPayload(**plan.allocation))

    return router
