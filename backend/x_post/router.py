from fastapi import APIRouter, HTTPException

from .agent import XPostAgent, XPostIdeaRequest, XPostInput

router = APIRouter(prefix="/x-post", tags=["X Workflow"])

try:
    agent = XPostAgent()
except Exception as exc:  # pragma: no cover - initialization errors logged only
    print(f"CRITICAL: Failed to initialize XPostAgent -> {exc}")
    agent = None


@router.post("/generate")
def generate_x_post(payload: XPostInput):
    if agent is None:
        raise HTTPException(
            status_code=500,
            detail="X Post workflow is not available. Check backend logs.",
        )

    try:
        return agent.invoke(payload)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/ideas")
def generate_x_post_ideas(payload: XPostIdeaRequest):
    if agent is None:
        raise HTTPException(
            status_code=500,
            detail="X Post workflow is not available. Check backend logs.",
        )

    try:
        return agent.generate_trending_ideas(payload)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


__all__ = ["router"]
