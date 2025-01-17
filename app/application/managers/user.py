from logging.config import dictConfig
from typing import Optional
import logging

from starlette.status import HTTP_400_BAD_REQUEST

from app.core.config import settings
from app.core.logger import LoggerConfig
from app.domain.models.auth import User
from fastapi import Request, HTTPException
from fastapi_users import BaseUserManager, IntegerIDMixin, models

dictConfig(LoggerConfig().model_dump())
logger: logging = logging.getLogger("digital_travel_concierge")

SECRET: str = settings.SECRET_JWT


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    """
    Custom user manager for handling user-related operations and token secrets.
    """

    reset_password_token_secret: str = SECRET
    verification_token_secret: str = SECRET

    async def get(self, id: models.ID) -> models.UP:
        """
        Get a user by id.

        :param id: Id. of the user to retrieve.
        :raises UserNotExists: The user does not exist.
        :return: A user.
        """
        user = await self.user_db.get(id)

        if user is None:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail={"user_id": f"User {id} does not exist."},
            )

        return user

    async def on_after_register(
        self,
        user: User,
        request: Optional[Request] = None,
    ):
        logger.info(
            "User %r has registered.",
            user.id,
        )
