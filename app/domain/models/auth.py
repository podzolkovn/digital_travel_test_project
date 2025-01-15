from typing import TYPE_CHECKING

from fastapi_users_db_sqlalchemy import (
    SQLAlchemyBaseUserTable,
    SQLAlchemyUserDatabase
)
from app.domain.models.abstract import AbstractModel
from fastapi_users_db_sqlalchemy.access_token import (
    SQLAlchemyBaseAccessTokenTable,
    SQLAlchemyAccessTokenDatabase
)
from sqlalchemy import (
    ForeignKey,
    Integer
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column
)

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class User(AbstractModel, SQLAlchemyBaseUserTable[int]):

    @property
    def role(self) -> str:
        return "admin" if self.is_superuser else "user"

    @classmethod
    def get_db(cls, session: "AsyncSession"):
        return SQLAlchemyUserDatabase(session, cls)


class AccessToken(AbstractModel, SQLAlchemyBaseAccessTokenTable[int]):
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), nullable=False)

    @classmethod
    def get_db(cls, session: "AsyncSession"):
        return SQLAlchemyAccessTokenDatabase(session, cls)
