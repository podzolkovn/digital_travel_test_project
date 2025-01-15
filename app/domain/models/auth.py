from typing import TYPE_CHECKING

from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable, SQLAlchemyUserDatabase
from app.domain.models.abstract import AbstractModel

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class User(AbstractModel, SQLAlchemyBaseUserTable[int]):

    @property
    def role(self) -> str:
        return "admin" if self.is_superuser else "user"

    @classmethod
    def get_db(cls, session: "AsyncSession"):
        return SQLAlchemyUserDatabase(session, User)
    