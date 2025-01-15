from typing import TYPE_CHECKING

from app.application.managers.user import UserManager
from app.domain.models.auth import User
from app.infrastructure.db import get_async_session
from fastapi import Depends

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


async def get_user_db(
    session: "AsyncSession" = Depends(get_async_session),
):
    yield User.get_db(session=session)


async def get_user_manager(
    user_db=Depends(get_user_db),
):
    yield UserManager(user_db)
