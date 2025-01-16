from typing import Optional

from fastapi import HTTPException
from starlette import status

from .abstract import AbstractReadSchemas, AbstractWriteUpdateSchemas
from .product import ProductRead, ProductWrite, ProductUpdate
from pydantic import field_validator

from app.domain.models.order import StatusEnum


class OrderBase(AbstractWriteUpdateSchemas):
    """
    Represents the base schema for order-related data including user_id, customer_name, and status.
    """

    customer_name: str
    status: str

    @field_validator("status")
    def validate_status(cls, value: str) -> str:
        if value.upper() not in StatusEnum.__members__:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "status": f"{value} is not a valid status. Available statuses are: "
                    f"{', '.join(StatusEnum.__members__.keys())}"
                },
            )
        return value


class OrderRead(AbstractReadSchemas, OrderBase):
    """
    Schema for reading an order including its associated products and total price.
    """

    id: int
    user_id: int
    total_price: float
    products: list[ProductRead]


class OrderWrite(OrderBase):
    """
    Schema for creating or writing a new order with associated products.
    """

    products: list[ProductWrite]

    @field_validator("products")
    def validate_products(cls, value: list[dict[str, str]]) -> list[dict[str, str]]:
        if len(value) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"products": "products must not be empty"},
            )
        return value


class OrderUpdate(OrderBase):
    """
    Schema for updating an order with optional fields and nested product updates.
    """

    user_id: Optional[int]
    customer_name: Optional[str]
    status: Optional[str]
    products: Optional[list[ProductUpdate]]
