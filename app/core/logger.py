from typing import Any

from pydantic import BaseModel


class LoggerConfig(BaseModel):
    """
    Configuration class for setting up application logging with customizable formatters, handlers, and loggers.
    """
    LOGGER_NAME: str = "digital_travel_concierge"
    LOG_FORMAT: str = "%(levelprefix)s | %(asctime)s | %(message)s"
    LOG_LEVEL: str = "DEBUG"

    # Logging config
    version: int = 1
    disable_existing_loggers: bool = False
    formatters: dict[str, dict[str, str]] = {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": LOG_FORMAT,
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    }
    handlers: dict[str, dict[str, str]] = {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
    }
    loggers: dict[str, dict[str, Any]] = {
        "ai_prompt": {"handlers": ["default"], "level": LOG_LEVEL, "propagate": False},
    }
