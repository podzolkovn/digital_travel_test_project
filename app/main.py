from logging.config import dictConfig

from fastapi import FastAPI

from app.core.logger import LoggerConfig
from app.presentation.api.main import router


def setup_logging():
    config = LoggerConfig()
    dictConfig(config.dict())


app: FastAPI = FastAPI()
setup_logging()
app.include_router(router)
