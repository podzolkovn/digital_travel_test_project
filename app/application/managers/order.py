from logging.config import dictConfig
import logging

from starlette import status
from starlette.responses import JSONResponse
from typing_extensions import Any

from app.core.logger import LoggerConfig
from app.domain.models import Order
from app.domain.repositories.orders import OrdersRepository
from app.domain.schemas.order import OrderRead
from app.domain.schemas.user import UserRead

dictConfig(LoggerConfig().model_dump())
logger: logging = logging.getLogger("digital_travel_concierge")


class OrderManager:
    def __init__(self, order_repository: OrdersRepository):
        self.order_repository = order_repository

    async def on_after_create_order(
        self,
        data: dict[Any, Any],
        user: UserRead,
    ) -> JSONResponse:
        data["user_id"] = user.id

        order: Order = await self.order_repository.create(data)
        order_read: OrderRead = OrderRead.model_validate(order)
        logger.info("Order created successfully by id %s", order.id)

        return JSONResponse(
            content=order_read.dict(),
            status_code=status.HTTP_201_CREATED,
        )
