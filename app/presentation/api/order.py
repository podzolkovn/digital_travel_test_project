from app.domain.models.auth import User
from app.domain.schemas.user import UserRead
from app.presentation.api.fastapi_users import current_user
from fastapi import APIRouter, Depends

router: APIRouter = APIRouter(
    prefix="/orders",
    tags=["Order"],
)


@router.get("")
async def get_orders(
    user: User = Depends(current_user),
):
    return {"message": "Hello World", "user": UserRead.model_validate(user)}
