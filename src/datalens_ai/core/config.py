"""Application configuration."""

from __future__ import annotations

import os
from pathlib import Path

from pydantic import BaseModel
from pydantic_settings import BaseSettings


class AIProviderConfig(BaseModel):
    """AI provider configuration."""

    default_provider: str = "mock"
    gemini_model: str = "gemini-2.0-flash"
    rate_limit_rpm: int = 15
    cache_enabled: bool = True
    max_retries: int = 2
    temperature: float = 0.1


class EngineConfig(BaseModel):
    """DuckDB engine configuration."""

    max_result_rows: int = 10000
    max_upload_size_mb: int = 100
    duckdb_memory_limit: str = "512MB"


class UIConfig(BaseModel):
    """UI configuration."""

    theme: str = "professional"
    max_chart_points: int = 5000
    show_sql: bool = True
    show_explanations: bool = True


class AppConfig(BaseSettings):
    """Root application config loaded from environment."""

    ai: AIProviderConfig = AIProviderConfig()
    engine: EngineConfig = EngineConfig()
    ui: UIConfig = UIConfig()
    model_config = {"env_prefix": "DATALENS_"}


def is_demo_mode() -> bool:
    """Check if running in demo mode (no API keys)."""
    if os.getenv("DATALENS_DEMO_MODE", "").lower() == "true":
        return True
    return not bool(os.getenv("GEMINI_API_KEY"))


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent.parent.parent


def get_data_dir() -> Path:
    """Get the data directory."""
    return get_project_root() / "data"


def get_available_providers() -> list[dict]:
    """List all providers with availability status."""
    return [
        {
            "name": "Gemini Flash",
            "key": "gemini",
            "available": bool(os.getenv("GEMINI_API_KEY")),
            "cost": "Free tier (15 RPM)",
        },
        {
            "name": "Mock Provider",
            "key": "mock",
            "available": True,
            "cost": "Free (rule-based)",
        },
    ]
