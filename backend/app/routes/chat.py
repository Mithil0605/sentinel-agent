from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field

from ..agent import AgentOrchestrator
from ..core.config import settings
from ..core.ratelimit import SlidingWindowRateLimiter

logger = logging.getLogger("sentinel.routes.chat")

router = APIRouter()
bearer = HTTPBearer(auto_error=False)
rate_limiter = SlidingWindowRateLimiter(settings.RATE_LIMIT_PER_MINUTE)

orchestrator: AgentOrchestrator | None = None


def get_orchestrator() -> AgentOrchestrator:
    global orchestrator
    if orchestrator is None:
        orchestrator = AgentOrchestrator()
    return orchestrator


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=settings.MAX_MESSAGE_LENGTH)
    session_id: str = Field(default="default", max_length=64)


class ChatResponse(BaseModel):
    response: str
    session_id: str
    turns: list[dict[str, Any]] = Field(default_factory=list)
    duration_ms: int = 0


@router.post("/chat", response_model=ChatResponse)
async def chat(
    payload: ChatRequest,
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
) -> ChatResponse:
    client_key = request.client.host if request.client else "unknown"
    allowed, retry = rate_limiter(client_key)
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Retry after {retry}s.",
            headers={"Retry-After": str(retry)},
        )

    agent = get_orchestrator()
    result = await agent.run(payload.session_id, payload.message)
    return ChatResponse(
        response=result.get("final", ""),
        session_id=payload.session_id,
        turns=result.get("turns", []),
        duration_ms=result.get("duration_ms", 0),
    )
