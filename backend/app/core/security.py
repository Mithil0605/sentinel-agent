import re
import bleach
import markupsafe

HTML_ALLOWED_TAGS = [
    "p", "br", "b", "i", "em", "strong", "ul", "ol", "li",
    "code", "pre", "blockquote", "h1", "h2", "h3", "h4",
    "a", "table", "thead", "tbody", "tr", "th", "td",
]
HTML_ALLOWED_ATTRIBUTES = {"a": ["href", "target", "rel"]}

# Patterns used to redact secrets before they reach the model or logs.
SECRET_PATTERNS = [
    re.compile(r"(?i)(api[_-]?key|secret|password|token|authorization)\s*[:=]\s*[\"']?([A-Za-z0-9_\-\.]{8,})"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bAIza[0-9A-Za-z_\-]{35}\b"),
]


def sanitize_html(value: str) -> str:
    return bleach.clean(
        value,
        tags=HTML_ALLOWED_TAGS,
        attributes=HTML_ALLOWED_ATTRIBUTES,
        strip=True,
    )


def escape_text(value: str) -> str:
    return markupsafe.escape(value)


def redact_secrets(value: str) -> str:
    for pattern in SECRET_PATTERNS:
        value = pattern.sub(lambda m: f"{m.group(1)}=[REDACTED]", value)
    return value


def strip_control_characters(value: str) -> str:
    return "".join(ch for ch in value if ch >= " " or ch in "\n\t")
