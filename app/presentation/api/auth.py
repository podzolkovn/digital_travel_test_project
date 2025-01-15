from app.core.security import authentication_backend
from app.domain.schemas.user import UserRead, UserCreate
from app.presentation.api.fastapi_users import fastapi_users
from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer

http_bearer: HTTPBearer = HTTPBearer(auto_error=False)

router: APIRouter = APIRouter(
    prefix="/auth",
    tags=["Auth"],
    dependencies=[
        Depends(http_bearer),
    ],
)

router.include_router(
    router=fastapi_users.get_auth_router(authentication_backend),
)


router.include_router(
    fastapi_users.get_register_router(
        UserRead,
        UserCreate,
    ),
)
