from fastapi_users import FastAPIUsers
from app.core.security import authentication_backend
from app.domain.dependencies.user import get_user_manager
from app.domain.models.auth import User


fastapi_users: FastAPIUsers = FastAPIUsers[User, int](
    get_user_manager,
    [authentication_backend],
)
