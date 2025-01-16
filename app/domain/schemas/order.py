import decimal
from typing import Optional
from .abstract import AbstractSchemas
from .product import ProductRead, ProductWrite, ProductUpdate


class OrderBase(AbstractSchemas):
    """
    Represents the base schema for order-related data including user_id, customer_name, and status.
    """

    user_id: int
    customer_name: str
    status: str


class OrderRead(OrderBase):
    """
    Schema for reading an order including its associated products and total price.
    """

    id: int
    total_price: decimal.Decimal
    products: list[ProductRead]


class OrderWrite(OrderBase):
    """
    Schema for creating or writing a new order with associated products.
    """

    products: list[ProductWrite]


class OrderUpdate(OrderBase):
    """
    Schema for updating an order with optional fields and nested product updates.
    """

    user_id: Optional[int]
    customer_name: Optional[str]
    status: Optional[str]
    products: Optional[list[ProductUpdate]]
