from typing import TYPE_CHECKING

from app.domain.models.auth import AccessToken
from app.infrastructure.db import get_async_session
from fastapi import Depends

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


async def get_access_token_db(session: "AsyncSession" = Depends(get_async_session)):
    yield AccessToken.get_db(session=session)
