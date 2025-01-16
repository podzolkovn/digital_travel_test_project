import decimal
from typing import Optional
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

    ...


class ProductUpdate(ProductBase):
    """
    Schema for updating product details with optional fields for name, price, and quantity.
    """

    name: Optional[str]
    price: Optional[decimal.Decimal]
    quantity: Optional[int]
