from __future__ import annotations

import json
from typing import Any, Callable


class ToolDefinition:
    def __init__(
        self,
        name: str,
        description: str,
        parameters: dict[str, Any],
        handler: Callable[..., dict[str, Any]],
    ):
        self.name = name
        self.description = description
        self.parameters = parameters
        self.handler = handler

    def schemas_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
        }


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, ToolDefinition] = {}

    def register(self, definition: ToolDefinition) -> None:
        self._tools[definition.name] = definition

    def list(self) -> list[ToolDefinition]:
        return list(self._tools.values())

    def schemas(self) -> list[dict[str, Any]]:
        return [t.schemas_dict() for t in self._tools.values()]

    def invoke(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        tool = self._tools.get(name)
        if tool is None:
            return {"error": f"Unknown tool: {name}", "success": False}
        try:
            return tool.handler(**arguments)
        except TypeError as exc:
            return {"error": f"Invalid arguments for {name}: {exc}", "success": False}
        except Exception as exc:  # noqa: BLE001
            return {"error": f"Tool {name} failed: {exc}", "success": False}

    def local_engine(self):
        from ..ai.local_engine import LocalEngine

        return LocalEngine(self)


_registry: ToolRegistry | None = None


def get_tool_registry() -> ToolRegistry:
    global _registry
    if _registry is None:
        _registry = build_registry()
    return _registry


def build_registry() -> ToolRegistry:
    from . import calculator, weather, time_tool, tickets, knowledge

    registry = ToolRegistry()
    registry.register(calculator.definition())
    registry.register(weather.definition())
    registry.register(time_tool.definition())
    registry.register(tickets.definition())
    registry.register(knowledge.definition())
    return registry


def tool_result_to_text(result: dict[str, Any]) -> str:
    if "error" in result and result.get("success") is False:
        return f"Error: {result['error']}"
    try:
        return json.dumps(result)
    except Exception:
        return str(result)
