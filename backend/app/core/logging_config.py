"""Structured logging configuration for production."""

from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Any

from app.core.config import settings


class JSONFormatter(logging.Formatter):
    """
    JSON formatter for structured logging in production.

    Outputs logs as JSON objects for easier parsing by log aggregation tools.
    """

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_obj: dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)

        # Add request_id if available (from middleware)
        if hasattr(record, "request_id"):
            log_obj["request_id"] = record.request_id

        # Add extra fields
        if hasattr(record, "extra"):
            log_obj["extra"] = record.extra

        return json.dumps(log_obj)


def setup_logging() -> None:
    """
    Configure logging for the application.

    - Development: human-readable format
    - Production: JSON format for log aggregation
    """
    handler = logging.StreamHandler()

    if settings.environment == "production":
        # Production: JSON structured logs
        handler.setFormatter(JSONFormatter())
    else:
        # Development: human-readable logs
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)

    # Configure root logger
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
    logging.basicConfig(
        level=log_level,
        handlers=[handler],
        force=True,  # Override any existing configuration
    )

    # Reduce noise from third-party loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
