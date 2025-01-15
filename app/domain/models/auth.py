import enum
from sqlalchemy import String, Enum
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.models.abstract import AbstractModel


class UserRoles(enum.Enum):
    """
    Enum representing different roles a user can have.
    """
    ADMIN: str = 'ADMIN'
    USER: str = 'USER'


class User(AbstractModel):
    """
    User model representing a user with email, password, and role.
    """
    __tablename__ = 'users'
    email: Mapped[str] = mapped_column(String(length=255), nullable=False)
    password: Mapped[str] = mapped_column(String(length=1024), nullable=False)
    role: Mapped[UserRoles] = mapped_column(Enum(UserRoles), nullable=False)
