from __future__ import annotations

from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        ser_json_exclude_none=True,
    )

    app_name: str = "MCP-One"
    app_version: str = "0.1.0"
    app_env: str = "local"
    debug: bool = True

    active_provider: str = "none"
    provider_timeout_seconds: float = 10.0

    openai_model: str = "gpt-4.1-mini"
    anthropic_model: str = "claude-haiku-4-5"

    enable_composition: bool = True
    enable_preview_for_planned: bool = True
    enable_handoff_for_planned: bool = True
    enable_handoff_for_disabled: bool = True

    enable_provider_enrichment: bool = False
    provider_enrichment_modes_raw: str = "summary,preview,composed_summary"

    enable_structured_logging: bool = True
    enable_debug_routes: bool = True
    enable_metrics_routes: bool = True
    enable_recent_resolutions_route: bool = True

    default_confidence_floor: float = 0.15
    default_confidence_cap: float = 0.95

    registry_source: str = "local"
    log_level: str = "INFO"

    cryptolink_base_url: str = "https://cryptolink.mx"
    cryptolink_app_url: str = "https://cryptolink-production.up.railway.app"
    cryptolink_api_key: str | None = Field(default=None)
    cryptolink_timeout_seconds: float = 6.0

    openai_api_key: str | None = Field(default=None)
    anthropic_api_key: str | None = Field(default=None)

    @property
    def provider_enrichment_modes(self) -> list[str]:
        return [
            item.strip()
            for item in self.provider_enrichment_modes_raw.split(",")
            if item.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    return Settings()