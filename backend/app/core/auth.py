from __future__ import annotations

import hashlib
import hmac
import secrets

from ..core.config import settings


def _derive_key(material: str) -> bytes:
    return hashlib.sha256(material.encode()).digest()


def generate_api_token() -> str:
    return secrets.token_urlsafe(32)


def hash_token(token: str) -> str:
    return hmac.new(_derive_key(settings.SECRET_KEY or "sentinel-dev"), token.encode(), hashlib.sha256).hexdigest()
