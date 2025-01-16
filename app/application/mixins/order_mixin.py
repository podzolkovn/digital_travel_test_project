from logging.config import dictConfig
import logging
from typing import TYPE_CHECKING

from fastapi import HTTPException
from starlette.status import HTTP_404_NOT_FOUND

from app.core.logger import LoggerConfig

from app.domain.repositories.orders import OrdersRepository
from app.domain.schemas.user import UserRead

if TYPE_CHECKING:
    from app.domain.models import Order


dictConfig(LoggerConfig().model_dump())
logger: logging = logging.getLogger("digital_travel_concierge")


class OrderMixin:
    def __init__(self, order_repository: OrdersRepository) -> None:
        self.order_repository = order_repository

    async def get_order_or_404(self, pk: int, user: UserRead) -> "Order":
        """
        Retrieve an order by its ID and the current user. If not found, raise HTTP 404.
        """
        order: "Order" = await self.order_repository.get_by_id_by_current_user(
            pk, user.id
        )
        if order is None:
            logger.info("Order %s not found for user %s", pk, user.id)
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND,
                detail={"order": f"Not Found by id: {pk}"},
            )
        return order
