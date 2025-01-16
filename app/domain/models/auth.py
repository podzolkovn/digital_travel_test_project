from typing import TYPE_CHECKING

from app.infrastructure.db import Base
from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable, SQLAlchemyUserDatabase
from app.domain.models.abstract import AbstractModel
from fastapi_users_db_sqlalchemy.access_token import (
    SQLAlchemyBaseAccessTokenTable,
    SQLAlchemyAccessTokenDatabase,
)
from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from app.domain.models.order import Order


class User(AbstractModel, SQLAlchemyBaseUserTable[int]):
    """
    Represents a user with additional role-based property and database utility method.
    """

    orders: Mapped[list["Order"]] = relationship(back_populates="user")

    @property
    def role(self) -> str:
        """
        Returns the user's role as 'admin' if superuser, otherwise 'user'.
        """
        return "admin" if self.is_superuser else "user"

    @classmethod
    def get_db(cls, session: "AsyncSession"):
        """
        Returns an SQLAlchemyUserDatabase instance for interacting with user data.
        """
        return SQLAlchemyUserDatabase(session, cls)


class AccessToken(Base, SQLAlchemyBaseAccessTokenTable[int]):
    """
    Represents an access token associated with a user.
    """

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), nullable=False)

    @classmethod
    def get_db(cls, session: "AsyncSession"):
        """
        Returns an SQLAlchemyAccessTokenDatabase instance for interacting with access token data.
        """
        return SQLAlchemyAccessTokenDatabase(session, cls)
