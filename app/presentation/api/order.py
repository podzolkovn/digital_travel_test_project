from starlette import status

from fastapi import APIRouter, Depends, Response, Request
from starlette.responses import JSONResponse

from app.application.managers.order import OrderManager
from app.domain.dependencies.order import get_order_db
from app.domain.models.auth import User
from app.domain.repositories.orders import OrdersRepository
from app.domain.schemas.order import OrderWrite, OrderRead, OrderUpdate
from app.domain.schemas.user import UserRead
from app.presentation.api.fastapi_users import current_user


router: APIRouter = APIRouter(
    prefix="/orders",
    tags=["Order"],
)


@router.post(
    path="",
    dependencies=[Depends(current_user)],
    response_model=OrderRead,  # Ensure the model matches the response type
    status_code=status.HTTP_201_CREATED,
)
async def create_orders(
    data: OrderWrite,
    user: UserRead = Depends(current_user),
    order_repository: OrdersRepository = Depends(get_order_db),
) -> JSONResponse:
    order_manager: OrderManager = OrderManager(order_repository=order_repository)
    order_data: JSONResponse = await order_manager.on_after_create_order(
        data=data.model_dump(),
        user=user,
    )
    return order_data


@router.get(
    path="",
    response_model=OrderRead,
    status_code=status.HTTP_200_OK,
)
async def get_orders(user: User = Depends(current_user)) -> Response:
    return Response(
        content="Hello World",
        media_type="application",
        status_code=status.HTTP_200_OK,
    )


@router.get(
    "/{order_id}",
    response_model=OrderRead,
    status_code=status.HTTP_200_OK,
)
async def get_order(
    order_id: int,
    user: User = Depends(current_user),
) -> Response:
    return Response(
        content="Hello World",
        media_type="application",
        status_code=status.HTTP_200_OK,
    )


@router.patch(
    "/{order_id}",
    response_model=OrderUpdate,
    status_code=status.HTTP_200_OK,
)
async def update_order(
    order_id: int,
    user: User = Depends(current_user),
) -> Response:
    return Response(
        content="Hello World",
        media_type="application",
        status_code=status.HTTP_200_OK,
    )


@router.delete(
    "/{order_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_order(
    order_id: int,
    user: User = Depends(current_user),
) -> Response:
    return Response(
        content="Hello World",
        media_type="application",
        status_code=status.HTTP_204_NO_CONTENT,
    )
