from logging.config import dictConfig
import logging
from typing import TYPE_CHECKING, Optional

from starlette.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
)
from starlette.responses import JSONResponse
from typing_extensions import Any

from app.application.mixins.order_mixin import OrderMixin
from app.core.logger import LoggerConfig
from app.domain.schemas.order import OrderRead
from app.domain.schemas.user import UserRead

if TYPE_CHECKING:
    from app.domain.models import Order
    from app.application.managers.user import UserManager

dictConfig(LoggerConfig().model_dump())
logger: logging = logging.getLogger("digital_travel_concierge")


class OrderManager(OrderMixin):

    async def on_after_create_order(
        self,
        data: dict[Any, Any],
        user: UserRead,
    ) -> JSONResponse:
        data["user_id"] = user.id

        order: "Order" = await self.order_repository.create(data)
        order_read: OrderRead = OrderRead.model_validate(order)
        logger.info("Order created successfully by id %s", order.id)

        return JSONResponse(
            content=order_read.dict(),
            status_code=HTTP_201_CREATED,
        )

    async def get_details(
        self,
        pk: int,
        user: UserRead,
    ) -> JSONResponse:
        order: "Order" = await self.get_order_or_404(pk, user)
        order_read: OrderRead = OrderRead.model_validate(order)

        logger.info("Order %s founded successfully by id %s", pk, order.id)
        return JSONResponse(
            content=order_read.dict(),
            status_code=HTTP_200_OK,
        )

    async def soft_delete(
        self,
        pk: int,
        user: UserRead,
    ) -> JSONResponse:
        order: "Order" = await self.get_order_or_404(pk, user)
        await self.order_repository.delete(order)

        return JSONResponse(
            status_code=HTTP_200_OK,
            content={"order": f"Order {pk} deleted soft"},
        )

    async def filter_orders(
        self,
        user: UserRead,
        filters: dict[str, Any],
    ) -> JSONResponse:
        await self.check_filters(user, filters)
        orders: list["Order"] = await self.order_repository.get_by_filter_or_get_all(
            filters=filters
        )
        orders_data: Optional[list[dict[Any, Any]]] = [
            OrderRead.model_validate(order).dict() for order in orders
        ]

        return JSONResponse(
            status_code=HTTP_200_OK,
            content=orders_data,
        )

    async def on_after_update(
        self,
        pk: int,
        user: UserRead,
        data: dict[Any, Any],
        user_manager: "UserManager",
    ) -> JSONResponse:
        order: "Order" = await self.get_order_or_404(pk, user)

        await self.validate_data_for_update(user, data, user_manager)

        order_update: "Order" = await self.order_repository.update(order, data)
        order_read: OrderRead = OrderRead.model_validate(order_update)
        return JSONResponse(
            status_code=HTTP_200_OK,
            content=order_read.dict(),
        )
