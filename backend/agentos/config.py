"""Local settings; secrets are read only on the backend."""
import os
from pathlib import Path


def database_path() -> Path:
    return Path(os.getenv("AGENTOS_DB_PATH", "./.agentos/state.sqlite3")).expanduser()


def model_settings() -> dict[str, str] | None:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    model = os.getenv("AGENTOS_MODEL", "").strip()
    if not api_key or not model:
        return None
    return {
        "api_key": api_key,
        "model": model,
        "base_url": os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/"),
    }
