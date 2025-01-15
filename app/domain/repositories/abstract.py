from sqlalchemy import Result, Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Generic, Type, TypeVar, Optional, List, Any

# Generic type for models
T = TypeVar("T")


class BaseRepository(Generic[T]):
    """
    Generic repository for database operations with SQLAlchemy models,
    including support for soft deletion.
    """
    def __init__(self, session: AsyncSession, model: Type[T]):
        self.session = session
        self.model = model

    async def get_by_id(self, object_id: int) -> Optional[T]:
        """
        Get an object by its ID, excluding soft-deleted objects.
        """
        result: Result[T] = await self.session.execute(
            select(self.model).where(self.model.id == object_id, self.model.is_deleted is False)
        )
        return result.scalars().first()

    async def get_all(self, limit: int = 100, offset: int = 0) -> List[T]:
        """
        Get all objects with optional limit and offset, excluding soft-deleted objects.
        """
        result: Result[T] = await self.session.execute(
            select(self.model).where(self.model.is_deleted is False).limit(limit).offset(offset)
        )
        return result.scalars().all()

    async def filter_by(self, filters: dict[str, Any], limit: int = 100, offset: int = 0) -> List[T]:
        """
        Filter objects based on the provided dictionary of filters, with optional limit and offset.
        """
        query: Select = select(self.model).where(self.model.is_deleted.is_(False))

        # Apply filters dynamically
        for field, value in filters.items():
            query = query.where(getattr(self.model, field) == value)

        query = query.limit(limit).offset(offset)
        result: Result[T] = await self.session.execute(query)
        return result.scalars().all()

    async def create(self, obj_data: dict[Any, Any]) -> T:
        """
        Create a new object using a dictionary of data and add it to the session.
        """
        obj: T = self.model(**obj_data)
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def update(self, obj: T, update_data: dict[Any, Any]) -> T:
        """
        Update an existing object with the provided data.
        """
        for key, value in update_data.items():
            setattr(obj, key, value)
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def delete(self, obj: T) -> None:
        """
        Perform a soft delete by setting is_deleted to True.
        """
        setattr(obj, "is_deleted", True)
        self.session.add(obj)
        await self.session.commit()
