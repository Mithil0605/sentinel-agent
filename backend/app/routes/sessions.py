from __future__ import annotations

import math
from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..models.database import get_db, ChatMessage

router = APIRouter()


@router.get("")
async def list_sessions(
    db: Session = Depends(get_db),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> dict[str, Any]:
    rows = (
        db.query(ChatMessage.session_id)
        .distinct()
        .order_by(ChatMessage.session_id)
        .offset(offset)
        .limit(limit)
        .all()
    )
    session_ids = [r[0] for r in rows]
    return {"sessions": session_ids, "count": len(session_ids)}


@router.get("/{session_id}/messages")
async def get_messages(
    session_id: str,
    db: Session = Depends(get_db),
    limit: int = Query(default=50, ge=1, le=500),
) -> dict[str, Any]:
    rows = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.id.desc())
        .limit(limit)
        .all()
    )
    rows = list(reversed(rows))
    return {
        "session_id": session_id,
        "messages": [
            {"role": m.role, "content": m.content, "created_at": m.created_at.isoformat()}
            for m in rows
        ],
    }
