import enum
import decimal
from typing import TYPE_CHECKING

from sqlalchemy import String, Enum, Integer, Numeric, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.models.abstract import AbstractModel
from app.domain.repositories.orders import OrdersRepository

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class StatusEnum(enum.Enum):
    """
    Enum representing different status an order can have.
    """

    PENDING: str = "PENDING"
    CONFIRMED: str = "CONFIRMED"
    CANCELLED: str = "CANCELLED"


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
        default=decimal.Decimal(
            "0.00",
        ),
    )
    order_products = relationship(
        "OrderProduct",
        back_populates="product",
    )
    orders = relationship(
        "Order",
        secondary="order_products",
        back_populates="products",
    )


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
    order_products = relationship(
        "OrderProduct",
        back_populates="order",
    )
    products = relationship(
        "Product",
        secondary="order_products",
        back_populates="orders",
    )

    @classmethod
    def get_db(cls, session: "AsyncSession"):
        """
        Returns an OrdersRepository instance for interacting with order data.
        """
        return OrdersRepository(session, cls)


class OrderProduct(AbstractModel):
    """
    Intermediate table to represent the many-to-many relationship between Order and Product,
    including additional fields like quantity.
    """

    __tablename__ = "order_products"
    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id"),
        nullable=False,
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id"),
        nullable=False,
    )

    # Optional: Add relationships if needed for direct access
    order = relationship(
        "Order",
        back_populates="order_products",
    )
    product = relationship(
        "Product",
        back_populates="order_products",
    )
