from __future__ import annotations

import json
import logging
from typing import Any

from app.config.settings import get_settings


LOGGER_NAME = "mcp_one"


def get_logger() -> logging.Logger:
    logger = logging.getLogger(LOGGER_NAME)

    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

    return logger


def log_event(event_name: str, payload: dict[str, Any]) -> None:
    settings = get_settings()
    if not settings.enable_structured_logging:
        return

    logger = get_logger()
    logger.info(
        json.dumps(
            {
                "event": event_name,
                **payload,
            },
            ensure_ascii=False,
        )
    )