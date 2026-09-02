from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from ..core.config import settings
from ..tools.registry import get_tool_registry

router = APIRouter()


@router.get("/health")
async def health() -> dict[str, Any]:
    return {"status": "ok", "app": settings.APP_NAME, "version": settings.APP_VERSION}


@router.get("/tools")
async def list_tools() -> dict[str, Any]:
    registry = get_tool_registry()
    return {"tools": registry.schemas()}
