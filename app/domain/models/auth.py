from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from app.domain.models.abstract import AbstractModel


class User(AbstractModel, SQLAlchemyBaseUserTable[int]):

    @property
    def role(self) -> str:
        return "admin" if self.is_superuser else "user"
