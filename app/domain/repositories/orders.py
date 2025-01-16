from typing import Any, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from .abstract import BaseRepository


T = TypeVar("T")


class OrdersRepository(BaseRepository):
    async def create(self, obj_data: dict[Any, Any]) -> T:
        from app.domain.models.product import Product

        products_data: list[dict[str, str]] = obj_data.pop("products")
        order: T = self.model(**obj_data)
        self.session.add(order)

        try:
            await self.session.commit()
        except Exception as e:
            await self.session.rollback()
            raise e

        for product_data in products_data:
            product: Product = Product(**product_data)
            self.session.add(product)

            try:
                await self.session.commit()
            except Exception as e:
                await self.session.rollback()
                raise e

            order: T = await self.session.scalar(
                select(self.model)
                .where(self.model.id == order.id)
                .options(
                    selectinload(self.model.products),
                )
            )

            order.products.append(product)

            try:
                await self.session.commit()
            except Exception as e:
                await self.session.rollback()
                raise e

        stmt = (
            select(self.model)
            .where(self.model.id == order.id)
            .options(
                selectinload(self.model.products),
            )
        )
        order: T = await self.session.execute(stmt)
        return order.scalar_one_or_none()
