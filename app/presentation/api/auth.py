from app.core.security import authentication_backend
from app.domain.schemas.user import UserRead, UserCreate
from app.presentation.api.fastapi_users import fastapi_users
from fastapi import APIRouter


# Router for authentication and registration endpoints.
router: APIRouter = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)


# Include login and logout routes using the authentication backend.
router.include_router(
    router=fastapi_users.get_auth_router(authentication_backend),
)

# Include registration routes for creating new users.
router.include_router(
    fastapi_users.get_register_router(
        UserRead,
        UserCreate,
    ),
)
