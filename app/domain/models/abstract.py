from datetime import datetime

from app.infrastructure.db import Base
from sqlalchemy import Integer, DateTime, func, Boolean
from sqlalchemy.orm import Mapped, mapped_column


class AbstractModel(Base):
    """
    An abstract base model providing common fields for ID, creation, update timestamps, and a soft delete flag.
    """
    __abstract__ = True
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now(),
                                                 onupdate=func.now())
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
