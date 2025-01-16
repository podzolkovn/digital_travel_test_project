from logging.config import dictConfig
import logging

from fastapi import HTTPException
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

    async def get_details(
        self,
        pk: int,
        user: UserRead,
    ) -> JSONResponse:
        order: Order = await self.order_repository.get_by_id_by_current_user(
            pk, user.id
        )
        if order is None:
            logger.info("Order %s not found for user %s", pk, user.id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"order": f"Not Found by id: {pk}"},
            )

        order_read: OrderRead = OrderRead.model_validate(order)

        logger.info("Order %s founded successfully by id %s", pk, order.id)
        return JSONResponse(
            content=order_read.dict(),
            status_code=status.HTTP_200_OK,
        )
