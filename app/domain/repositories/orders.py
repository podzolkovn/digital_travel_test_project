from typing import Any, TypeVar, Optional, Type

from sqlalchemy import select, and_, Result, Select, ScalarResult
from sqlalchemy.orm import selectinload

from .abstract import BaseRepository


T = TypeVar("T")


class OrdersRepository(BaseRepository):
    async def create(self, obj_data: dict[Any, Any]) -> T:
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
        self, object_id: int, user_id: int
    ) -> Optional[T]:
        stmt: Select = (
            select(self.model)
            .where(
                self.model.id == object_id,
                self.model.user_id == user_id,
                self.model.is_deleted is False,
            )
            .options(selectinload(self.model.products))
        )
        result: Result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_filter_or_get_all(
        self,
        filters: dict[str, Optional[Any]],
    ) -> list[T]:

        conditions: list[Any] = []
        if "status" in filters and filters["status"] is not None:
            conditions.append(self.model.status == filters["status"])
        if "min_price" in filters and filters["min_price"] is not None:
            conditions.append(self.model.total_price >= filters["min_price"])
        if "max_price" in filters and filters["max_price"] is not None:
            conditions.append(self.model.total_price <= filters["max_price"])
        if "user_id" in filters and filters["user_id"] is not None:
            conditions.append(self.model.user_id == filters["user_id"])

        conditions.append(self.model.is_deleted is False)

        stmt: Select = (
            select(self.model)
            .where(and_(*conditions))
            .options(selectinload(self.model.products))
        )
        result: ScalarResult[T] = await self.session.scalars(stmt)
        return result.all()
