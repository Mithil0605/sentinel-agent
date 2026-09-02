import re
from typing import Any


class ToolCall:
    def __init__(self, name: str, arguments: dict[str, Any]):
        self.name = name
        self.arguments = arguments


def extract_tool_call(text: str) -> ToolCall | None:
    """Parse a structured tool invocation of the form:
    <function>{name: "tool_name", arguments: {"key": "value"}}</function>
    Also accepts a JSON action block.
    """
    text = text.strip()

    m = re.search(
        r"<function>\s*(.*?)\s*</function>", text, re.DOTALL | re.IGNORECASE
    )
    if not m:
        return None

    body = m.group(1).strip()
    name_m = re.search(r'name\s*[:=]\s*"?([a-zA-Z0-9_]+)"?', body)
    if not name_m:
        return None

    name = name_m.group(1)
    args_m = re.search(
        r"arguments\s*[:=]\s*(\{.*\})", body, re.DOTALL
    )
    arguments: dict[str, Any] = {}
    if args_m:
        try:
            import json

            arguments = json.loads(args_m.group(1))
            if not isinstance(arguments, dict):
                arguments = {}
        except Exception:
            arguments = {}
    return ToolCall(name, arguments)
