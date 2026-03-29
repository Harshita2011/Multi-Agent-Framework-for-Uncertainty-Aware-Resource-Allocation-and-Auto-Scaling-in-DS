"""FastAPI routes for the resource service."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from .manager import ResourceManager, ResourceSnapshot


class ResourcesResponse(BaseModel):
    """Current node pool counts."""

    small: int
    medium: int
    large: int


class UpdateResourcesRequest(BaseModel):
    """Mutation request for the in-memory resource pool."""

    node_type: str
    count: int = 1


def create_router(manager: ResourceManager) -> APIRouter:
    """Expose resource tracking endpoints around the provided manager."""

    router = APIRouter()

    @router.get("/resources", response_model=ResourcesResponse)
    def get_resources() -> ResourcesResponse:
        return _to_response(manager.snapshot())

    @router.post("/resources/allocate", response_model=ResourcesResponse)
    def allocate_resources(request: UpdateResourcesRequest) -> ResourcesResponse:
        try:
            snapshot = manager.allocate(node_type=request.node_type, count=request.count)
        except ValueError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error
        return _to_response(snapshot)

    @router.post("/resources/release", response_model=ResourcesResponse)
    def release_resources(request: UpdateResourcesRequest) -> ResourcesResponse:
        try:
            snapshot = manager.release(node_type=request.node_type, count=request.count)
        except ValueError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error
        return _to_response(snapshot)

    return router


def _to_response(snapshot: ResourceSnapshot) -> ResourcesResponse:
    return ResourcesResponse(
        small=snapshot.small,
        medium=snapshot.medium,
        large=snapshot.large,
    )
