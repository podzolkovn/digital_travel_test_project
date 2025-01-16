from fastapi_users import FastAPIUsers
from app.core.security import authentication_backend
from app.domain.dependencies.user import get_user_manager
from app.domain.models.auth import User


# Initialize FastAPIUsers with a user manager and authentication backend.
fastapi_users: FastAPIUsers = FastAPIUsers[User, int](
    get_user_manager,
    [authentication_backend],
)


# Dependency to get the currently authenticated user, with optional activation.
current_user = fastapi_users.current_user(active=True)

# Dependency to get the currently authenticated superuser, with optional activation.
current_super_user = fastapi_users.current_user(active=True, superuser=True)
