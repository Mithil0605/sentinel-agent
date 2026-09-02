from __future__ import annotations

import hashlib
import time

from .registry import ToolDefinition


def create_ticket(summary: str, priority: str = "standard") -> dict:
    priority = priority.lower()
    if priority not in ("low", "standard", "high", "critical"):
        priority = "standard"
    digest = hashlib.sha256(f"{summary}:{time.time_ns()}".encode()).hexdigest()[:8]
    ticket_id = f"TK-{time.strftime('%Y%m%d')}-{digest.upper()}"
    return {
        "ticket_id": ticket_id,
        "summary": summary,
        "priority": priority,
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        "status": "open",
        "success": True,
    }


def definition() -> ToolDefinition:
    return ToolDefinition(
        name="create_ticket",
        description="Create an internal support ticket with a summary and priority.",
        parameters={
            "type": "object",
            "properties": {
                "summary": {"type": "string", "description": "Short description of the issue"},
                "priority": {
                    "type": "string",
                    "enum": ["low", "standard", "high", "critical"],
                    "description": "Severity of the ticket",
                    "default": "standard",
                },
            },
            "required": ["summary"],
        },
        handler=create_ticket,
    )
