from logging.config import dictConfig
from typing import Optional
import logging
from app.core.config import settings
from app.core.logger import LoggerConfig
from app.domain.models.auth import User
from fastapi import Request
from fastapi_users import BaseUserManager, IntegerIDMixin

dictConfig(LoggerConfig().model_dump())
logger: logging = logging.getLogger("digital_travel_concierge")

SECRET: str = settings.SECRET_JWT


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    """
    Custom user manager for handling user-related operations and token secrets.
    """

    reset_password_token_secret: str = SECRET
    verification_token_secret: str = SECRET

    async def on_after_register(
        self,
        user: User,
        request: Optional[Request] = None,
    ):
        logger.info(
            "User %r has registered.",
            user.id,
        )
