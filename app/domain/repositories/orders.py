from typing import Any, TypeVar, Optional

from sqlalchemy import select
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

        products = [Product(**product_data) for product_data in products_data]
        order.products.extend(products)

        try:
            await self.session.commit()
        except Exception as e:
            await self.session.rollback()
            raise e

        stmt = (
            select(self.model)
            .where(self.model.id == order.id)
            .options(selectinload(self.model.products))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id_by_current_user(
        self, object_id: int, user_id: int
    ) -> Optional[T]:
        stmt = (
            select(self.model)
            .where(
                self.model.id == object_id,
                self.model.user_id == user_id,
                self.model.is_deleted is False,
            )
            .options(selectinload(self.model.products))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
