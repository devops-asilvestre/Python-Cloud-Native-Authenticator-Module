from typing import TypedDict

from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["health"])


class LivenessResponse(TypedDict):
    status: str


@router.get("/live", response_model=None)
def liveness() -> LivenessResponse:
    return {"status": "ok"}
