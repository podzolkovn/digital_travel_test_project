import enum
import decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    String,
    Enum,
    Numeric,
    ForeignKey,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.models.abstract import AbstractModel


from .order_product import order_product_association_table


from app.domain.repositories.orders import OrdersRepository

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from . import User, Product


class StatusEnum(enum.Enum):
    """
    Enum representing different status an order can have.
    """

    PENDING: str = "PENDING"
    CONFIRMED: str = "CONFIRMED"
    CANCELLED: str = "CANCELLED"


class Order(AbstractModel):
    """
    Represents a customer order, including customer details, order status, total price, and associated products.
    """

    __tablename__ = "orders"
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id"),
    )
    customer_name: Mapped[str] = mapped_column(
        String(length=255),
        nullable=False,
    )
    status: Mapped[StatusEnum] = mapped_column(
        Enum(StatusEnum),
        default=StatusEnum.PENDING,
        nullable=True,
    )
    total_price: Mapped[decimal.Decimal] = mapped_column(
        Numeric(10, 2),
        default=decimal.Decimal("0.00"),
        nullable=True,
    )
    user: Mapped["User"] = relationship(back_populates="orders")
    products: Mapped[list["Product"]] = relationship(
        "Product",
        secondary=order_product_association_table,
        back_populates="orders",
        overlaps="products,order_products",
    )

    @classmethod
    def get_db(cls, session: "AsyncSession"):
        """
        Returns an OrdersRepository instance for interacting with order data.
        """
        return OrdersRepository(session, cls)
