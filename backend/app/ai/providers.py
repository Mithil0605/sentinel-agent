import json
import logging
from typing import Any

import httpx

from ..core.config import settings
from .parser import ToolCall

logger = logging.getLogger("sentinel.ai.openai")


class OpenAIProvider:
    name = "openai"

    def __init__(self, tool_schemas: list[dict[str, Any]]):
        self.base_url = settings.OPENAI_BASE_URL.rstrip("/")
        self.model = settings.OPENAI_MODEL
        self.tool_schemas = tool_schemas

    async def generate(self, messages: list[dict[str, Any]]) -> dict[str, Any]:
        payload_messages = []
        for m in messages:
            role = m.get("role")
            content = m.get("content", "")
            if role in ("system", "user", "assistant"):
                payload_messages.append({"role": role, "content": content})

        payload: dict[str, Any] = {
            "model": self.model,
            "messages": payload_messages,
            "temperature": 0.2,
        }
        if self.tool_schemas:
            payload["tools"] = [
                {
                    "type": "function",
                    "function": {
                        "name": t["name"],
                        "description": t["description"],
                        "parameters": t.get("parameters", {"type": "object", "properties": {}}),
                    },
                }
                for t in self.tool_schemas
            ]
            payload["tool_choice"] = "auto"

        headers = {
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
            "Content-Type": "application/json",
        }
        turns = []
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                f"{self.base_url}/chat/completions", json=payload, headers=headers
            )
            resp.raise_for_status()
            data = resp.json()

        choice = data["choices"][0]["message"]
        tool_calls = choice.get("tool_calls") or []
        text = choice.get("content") or ""

        for tc in tool_calls:
            try:
                args = json.loads(tc["function"]["arguments"] or "{}")
            except Exception:
                args = {}
            turns.append(
                {
                    "type": "tool_call",
                    "name": tc["function"]["name"],
                    "arguments": args,
                }
            )
        return {"turns": turns, "final": text}


def build_provider() -> Any:
    from ..tools.registry import get_tool_registry

    registry = get_tool_registry()
    if settings.AI_PROVIDER == "openai" and settings.OPENAI_API_KEY:
        return OpenAIProvider(registry.schemas())
    return registry.local_engine()
