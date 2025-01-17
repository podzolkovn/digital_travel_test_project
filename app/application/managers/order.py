import json
import logging
from logging.config import dictConfig

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
    """
    Manages operations related to orders, including creation, retrieval,
    updating, and deletion of orders. This class extends the OrderMixin
    to provide additional functionalities for handling orders in an asynchronous
    environment.
    """

    async def cache_order(self, order_id: int, data: dict[Any, Any]):
        await self._redis.set(f"order:{order_id}", json.dumps(data))

    async def get_cached_order(self, order_id: int):
        data_str = await self._redis.get(f"order:{order_id}")
        if data_str:
            return json.loads(data_str)
        return None

    async def delete_cached_order(self, order_id: int):
        await self._redis.delete(f"order:{order_id}")

    async def on_after_create_order(
        self,
        data: dict[Any, Any],
        user: UserRead,
    ) -> JSONResponse:
        """
        Creates a new order using the provided data and associates it with the given user.
        Once the order is created, it is validated and returned as a JSON response with
        a 201 Created status.
        """

        data["user_id"] = user.id

        order: "Order" = await self.order_repository.create(data)
        order_read: OrderRead = OrderRead.model_validate(order)

        await self.cache_order(order.id, order_read.dict())

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
        """
        Retrieves the details of an order based on its primary key (pk).
        The order is validated and returned as a JSON response with a 200 OK status.
        """
        cached_order = await self.get_cached_order(pk)
        if cached_order:
            order_read = OrderRead.model_validate(cached_order)
            logger.info("Order %s retrieved from cache", pk)
        else:
            order: "Order" = await self.get_order_or_404(pk, user)
            order_read: OrderRead = OrderRead.model_validate(order)
            await self.cache_order(order.id, order_read.dict())
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
        """
        Soft deletes an order based on its primary key (pk). This means the order is
        logically removed from the system but can be recovered if needed.
        The function returns a JSON response with a 200 OK status.
        """
        order: "Order" = await self.get_order_or_404(pk, user)
        await self.order_repository.delete(order)
        await self.delete_cached_order(pk)
        logger.info("Order %r deleted soft", pk)
        return JSONResponse(
            status_code=HTTP_200_OK,
            content={"order": f"Order {pk} deleted soft"},
        )

    async def filter_orders(
        self,
        user: UserRead,
        filters: dict[str, Any],
    ) -> JSONResponse:
        """
        Filters orders based on the provided criteria and retrieves them from
        the database. Each filtered order is validated and returned as a list
        of dictionaries in a JSON response with a 200 OK status.
        """
        await self.check_filters(user, filters)
        orders: list["Order"] = await self.order_repository.get_by_filter_or_get_all(
            filters=filters
        )
        orders_data: Optional[list[dict[Any, Any]]] = [
            OrderRead.model_validate(order).dict() for order in orders
        ]
        logger.info(
            "Orders data: IDs: %s, Total Count: %d",
            [order.id for order in orders],
            len(orders),
        )
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
        """
        Updates an existing order identified by its primary key (pk) with the
        provided data. After validation and successful update, the updated order
        is returned as a JSON response with a 200 OK status.
        """
        order: "Order" = await self.get_order_or_404(pk, user)

        await self.validate_data_for_update(user, data, user_manager)

        order_update: "Order" = await self.order_repository.update(order, data)
        order_read: OrderRead = OrderRead.model_validate(order_update)
        await self.cache_order(order_update.id, order_read.dict())
        logger.info("Order update: %s", order_read)
        return JSONResponse(
            status_code=HTTP_200_OK,
            content=order_read.dict(),
        )
