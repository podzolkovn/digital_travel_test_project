import os
from typing import Any
from pydantic import BaseModel


class LoggerConfig(BaseModel):
    """
    Configuration class for setting up application logging with customizable formatters, handlers, and loggers.
    """

    LOGGER_NAME: str = "digital_travel_concierge"
    LOG_FORMAT: str = "%(levelprefix)s | %(asctime)s | %(message)s"
    LOG_LEVEL: str = "DEBUG"

    LOG_DIR: str = "logs"
    LOG_FILE: str = "application.log"

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
    handlers: dict[str, dict[str, Any]] = {
        "console": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
        "file": {
            "formatter": "default",
            "class": "logging.FileHandler",
            "filename": f"{LOG_DIR}/{LOG_FILE}",
            "mode": "a",
        },
    }
    loggers: dict[str, dict[str, Any]] = {
        "digital_travel_concierge": {
            "handlers": ["console", "file"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
    }

    def __init__(self, **data: Any):
        super().__init__(**data)
        os.makedirs(self.LOG_DIR, exist_ok=True)
