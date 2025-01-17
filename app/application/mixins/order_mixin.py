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
from app.infrastructure.redis import get_redis

if TYPE_CHECKING:
    from app.domain.repositories.orders import OrdersRepository
    from aioredis import Redis
    from app.application.managers.user import UserManager
    from app.domain.schemas.user import UserRead
    from app.domain.models import Order

dictConfig(LoggerConfig().model_dump())
logger: logging = logging.getLogger("digital_travel_concierge")


class OrderMixin:
    """
    A mixin class that provides utility methods for managing orders, including
    retrieving, validating, and filtering orders based on user permissions and data.
    """

    def __init__(self, order_repository: "OrdersRepository", redis: "Redis") -> None:
        self.order_repository = order_repository
        self._redis = redis

    async def get_order_or_404(self, pk: int, user: "UserRead") -> "Order":
        """
        Retrieves an order by its ID and checks if the order belongs to the current user.
        If the order is not found, raises a 404 HTTP exception.
        Superusers are allowed to access any order by ID.
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
                detail={
                    "order": f"Not Found by id: {pk}",
                    "code": "not_found",
                },
            )
        return order

    async def check_filters(self, user: "UserRead", filters: dict[Any, Any]) -> None:
        """
        Validates the provided filters for orders, checking status and price ranges.
        Raises HTTP exceptions for invalid filters. If the user is not a superuser,
        adds the user ID to the filters.
        """
        status: Optional[str] = filters.get("status", None)
        min_price: Optional[int] = filters.get("min_price", None)
        max_price: Optional[int] = filters.get("max_price", None)

        if status is not None and status.upper() not in StatusEnum.__members__:
            logger.info(
                "Invalid choice for status: %s",
                status.upper(),
            )
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail={
                    "status": f"{status} is not a valid status. Available statuses are: "
                    f"{', '.join(StatusEnum.__members__.keys())}",
                    "code": "invalid_choice",
                },
            )

        if min_price is not None and max_price is not None and min_price > max_price:
            logger.info(
                "%r > %r The minimum price cannot be greater than the maximum price.",
                min_price,
                max_price,
            )
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail={
                    "error": "The minimum price cannot be greater than the maximum price.",
                    "code": "invalid_price_range",
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
        """
        Validates the data provided for updating an order.
        Checks if the data is empty or if unauthorized modifications are attempted on specific fields.
        """
        if len(data) == 0:
            logger.info(
                "Length == 0 for order. The request body cannot be empty. Please provide valid data."
            )
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail={
                    "error": "The request body cannot be empty. Please provide valid data.",
                    "code": "null",
                },
            )

        user_id: Optional[int] = data.get("user_id", None)
        if user_id and not user.is_superuser:
            logger.info(
                "User %r do not have permission to modify the user_id field.",
                user_id,
            )
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN,
                detail={
                    "user_id": "You do not have permission to modify the user_id field.",
                },
            )
        if user_id and user.is_superuser:
            await user_manager.get(user_id)
