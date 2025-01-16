import decimal
from pydantic import field_validator
from typing import Optional
from fastapi import HTTPException
from starlette import status

from .abstract import AbstractReadSchemas, AbstractWriteUpdateSchemas


class ProductBase(AbstractWriteUpdateSchemas):
    """
    Represents the base schema for product-related data with fields name, price, and quantity.
    """

    name: str
    price: float
    quantity: int


class ProductRead(AbstractReadSchemas, ProductBase):
    """
    Schema for reading product data with id, inherited from ProductBase.
    """

    id: int


class ProductWrite(ProductBase):
    """
    Schema for creating or writing product data.
    """

    @field_validator("quantity")
    def validate_quantity(cls, value: int) -> int:
        if value <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"quantity": "Quantity must be greater than zero."},
            )

        return value

    @field_validator("price")
    def validate_price(cls, value: float) -> float:
        if value <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"price": "Price must be greater than zero."},
            )
        return value


class ProductUpdate(ProductBase):
    """
    Schema for updating product details with optional fields for name, price, and quantity.
    """

    name: Optional[str]
    price: Optional[decimal.Decimal]
    quantity: Optional[int]
