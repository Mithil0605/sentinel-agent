from functools import lru_cache
import os
from pathlib import Path

try:
    from dotenv import load_dotenv

    load_dotenv(Path(__file__).resolve().parent.parent.parent.parent / ".env")
except Exception as exc:  # noqa: BLE001
    # dotenv is optional; fall back to environment variables only.
    print(f"Warning: could not load .env ({exc})")

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent


class Settings:
    APP_NAME: str = "Sentinel Agent"
    APP_VERSION: str = "1.0.0"

    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    # Bind to localhost by default; set HOST=0.0.0.0 explicitly in production
    # when the app is intentionally exposed behind a reverse proxy.
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
    )
    ALGORITHM: str = "HS256"

    SPACE_ID: str = os.getenv("SPACE_ID", "pri_sa_01")

    MAX_MESSAGE_LENGTH: int = int(os.getenv("MAX_MESSAGE_LENGTH", "4000"))
    MAX_CONVERSATION_TURNS: int = int(os.getenv("MAX_CONVERSATION_TURNS", "60"))
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "30"))

    ALLOWED_ORIGINS: list[str] = [
        o.strip()
        for o in os.getenv("ALLOWED_ORIGINS", "http://localhost:8000,http://127.0.0.1:8000").split(",")
        if o.strip()
    ]

    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "local")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", f"sqlite:///{BASE_DIR / 'sentinel.db'}"
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
