from typing import Any, TypeVar, Optional

from sqlalchemy import select, Result, Select, ScalarResult
from sqlalchemy.orm import selectinload

from .abstract import BaseRepository


T = TypeVar("T")


class OrdersRepository(BaseRepository):
    """
    A repository class for managing CRUD operations on Order objects in the database.
    Provides methods for creating, retrieving, and filtering orders, along with handling
    relationships and transactions.
    """

    async def create(self, obj_data: dict[Any, Any]) -> T:
        """
        Creates a new order from the provided data, including associated product details.
        Calculates the total price based on product prices and quantities.
        Commits the transaction to the database and returns the created order with product details.
        """
        from app.domain.models.product import Product

        products_data: list[dict[str, Any]] = obj_data.pop("products")
        obj_data["total_price"] = sum(
            product["price"] * product["quantity"] for product in products_data
        )

        order: T = self.model(**obj_data)
        self.session.add(order)

        products: list[Product] = [
            Product(**product_data) for product_data in products_data
        ]
        order.products.extend(products)

        try:
            await self.session.commit()
        except Exception as e:
            await self.session.rollback()
            raise e

        stmt: Select = (
            select(self.model)
            .where(self.model.id == order.id)
            .options(selectinload(self.model.products))
        )
        result: Result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id_by_current_user(
        self,
        object_id: int,
        user_id: Optional[int] = None,
    ) -> Optional[T]:
        """
        Retrieves an order by its ID, optionally filtered by the user ID.
        Ensures that only non-deleted orders are fetched.
        """
        conditions: list[Any] = []
        if user_id is not None:
            conditions.append(self.model.user_id == user_id)

        conditions.append(self.model.id == object_id)
        conditions.append(self.model.is_deleted == False)

        stmt: Select = (
            select(self.model)
            .where(*conditions)
            .options(selectinload(self.model.products))
        )
        result: Result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_filter_or_get_all(
        self,
        filters: dict[str, Optional[Any]],
    ) -> list[T]:
        """
        Retrieves orders based on the provided filters, or returns all non-deleted orders if no filters are given.
        Supports filtering by status, price range, and user ID. Includes related products in the result.
        """
        conditions: list[Any] = []
        if "status" in filters and filters["status"] is not None:
            conditions.append(self.model.status == filters["status"])
        if "min_price" in filters and filters["min_price"] is not None:
            conditions.append(self.model.total_price >= filters["min_price"])
        if "max_price" in filters and filters["max_price"] is not None:
            conditions.append(self.model.total_price <= filters["max_price"])
        if "user_id" in filters and filters["user_id"] is not None:
            conditions.append(self.model.user_id == filters["user_id"])

        conditions.append(self.model.is_deleted == False)

        stmt: Select = (
            select(self.model)
            .where(*conditions)
            .options(selectinload(self.model.products))
        )
        result: ScalarResult[T] = await self.session.scalars(stmt)
        return result.all()
