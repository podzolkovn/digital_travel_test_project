from typing import Any, TypeVar, Type

from sqlalchemy.ext.asyncio import AsyncSession

from .abstract import BaseRepository
from app.domain.models.main import Order, Product, OrderProduct

T = TypeVar("T")


class OrdersRepository(BaseRepository):
    def __init__(self, session: AsyncSession, model: Type[T]) -> None:
        super().__init__(session, model)
        self.model = Order

    async def create(self, obj_data: dict[Any, Any]) -> Order:
        async with self.session.begin():
            products: list[dict[str, str]] = obj_data.pop("products")
            order: Order = self.model(**obj_data)

            self.session.add(order)

            for product_data in products:
                product: Product = Product(**product_data)
                self.session.add(product)

                order_product: OrderProduct = OrderProduct(
                    order=order,
                    product=product,
                )
                self.session.add(order_product)

            await self.session.commit()

        return order
