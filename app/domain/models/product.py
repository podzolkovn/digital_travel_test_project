import decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    String,
    Integer,
    Numeric,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship


from app.domain.models.abstract import AbstractModel
from app.domain.models.order_product import order_product_association_table

if TYPE_CHECKING:
    from app.domain.models import Order


class Product(AbstractModel):
    """
    Represents a product available for purchase, including its name, quantity, price, and associated orders.
    """

    __tablename__ = "products"
    name: Mapped[str] = mapped_column(
        String(length=255),
        nullable=False,
    )
    quantity: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    price: Mapped[decimal.Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=decimal.Decimal("0.00"),
    )
    orders: Mapped[list["Order"]] = relationship(
        "Order",
        secondary=order_product_association_table,
        back_populates="products",
    )
