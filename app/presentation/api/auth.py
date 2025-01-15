from app.core.security import authentication_backend
from app.presentation.api.fastapi_users import fastapi_users
from fastapi import APIRouter


router: APIRouter = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)

router.include_router(
    router=fastapi_users.get_auth_router(authentication_backend),
)
