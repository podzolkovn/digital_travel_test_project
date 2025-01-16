from logging.config import dictConfig

from fastapi import FastAPI

from app.core.logger import LoggerConfig
from app.presentation.api.main import router


def setup_logging():
    """
    Configures logging using the LoggerConfig class.
    """
    config = LoggerConfig()
    dictConfig(config.dict())


app: FastAPI = FastAPI()

# Setup logging
setup_logging()

# Include the main router
app.include_router(router)
