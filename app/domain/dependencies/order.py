from typing import TYPE_CHECKING
from fastapi import Depends

from app.domain.models.main import Order
from app.infrastructure.db import get_async_session

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


async def get_order_db(
    session: "AsyncSession" = Depends(get_async_session),
):
    """
    Provides a database connection for working with order records.
    """
    yield Order.get_db(session=session)
