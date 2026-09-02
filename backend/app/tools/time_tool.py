from __future__ import annotations

import time

from .registry import ToolDefinition


def get_time() -> dict:
    return {
        "time": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
        "zone": "UTC",
        "success": True,
    }


def definition() -> ToolDefinition:
    return ToolDefinition(
        name="get_time",
        description="Return the current UTC date and time.",
        parameters={"type": "object", "properties": {}},
        handler=get_time,
    )
