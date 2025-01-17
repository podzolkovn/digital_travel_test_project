from logging.config import dictConfig
import logging
from typing import TYPE_CHECKING, Any, Optional

from fastapi import HTTPException
from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
)

from app.core.logger import LoggerConfig
from app.domain.models.order import StatusEnum

from app.domain.repositories.orders import OrdersRepository


if TYPE_CHECKING:
    from app.application.managers.user import UserManager
    from app.domain.schemas.user import UserRead
    from app.domain.models import Order

dictConfig(LoggerConfig().model_dump())
logger: logging = logging.getLogger("digital_travel_concierge")


class OrderMixin:
    def __init__(self, order_repository: OrdersRepository) -> None:
        self.order_repository = order_repository

    async def get_order_or_404(self, pk: int, user: "UserRead") -> "Order":
        """
        Retrieve an order by its ID and the current user. If not found, raise HTTP 404.
        """

        if user.is_superuser:
            order: "Order" = await self.order_repository.get_by_id_by_current_user(pk)
        else:
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

    async def check_filters(self, user: "UserRead", filters: dict[Any, Any]) -> None:
        status: Optional[str] = filters.get("status", None)
        min_price: Optional[int] = filters.get("min_price", None)
        max_price: Optional[int] = filters.get("max_price", None)

        if status is not None and status.upper() not in StatusEnum.__members__:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail={
                    "status": f"{status} is not a valid status. Available statuses are: "
                    f"{', '.join(StatusEnum.__members__.keys())}"
                },
            )

        if min_price is not None and max_price is not None and min_price > max_price:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail={
                    "error": "The minimum price cannot be greater than the maximum price.",
                },
            )

        if not user.is_superuser:
            filters["user_id"] = user.id

    async def validate_data_for_update(
        self,
        user: "UserRead",
        data: dict[Any, Any],
        user_manager: "UserManager",
    ):
        if len(data) == 0:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail={
                    "body": "The request body cannot be empty. Please provide valid data.",
                },
            )

        user_id: Optional[int] = data.get("user_id", None)
        if user_id and not user.is_superuser:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN,
                detail={
                    "user_id": "You do not have permission to modify the user_id field.",
                },
            )
        if user_id and user.is_superuser:
            await user_manager.get(user_id)
