from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    telegram_token: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    provider: str = os.getenv("LLM_PROVIDER", "mock")
    api_base_url: str = os.getenv("LLM_API_BASE_URL", "https://api.example.com/v1")
    api_key: str = os.getenv("LLM_API_KEY", "")
    model: str = os.getenv("LLM_MODEL", "example-model")
    database: Path = Path(os.getenv("APP_DATABASE", "runtime/learning.sqlite3"))

