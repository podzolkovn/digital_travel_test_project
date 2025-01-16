from starlette import status

from app.domain.models.auth import User
from app.domain.schemas.order import OrderWrite, OrderRead, OrderUpdate
from app.presentation.api.fastapi_users import current_user
from fastapi import APIRouter, Depends, Response

router: APIRouter = APIRouter(
    prefix="/orders",
    tags=["Order"],
)


@router.post(
    path="",
    response_model=OrderRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_orders(
    data: OrderWrite,
    user: User = Depends(current_user),
) -> Response:
    return Response(
        content="Hello World",
        media_type="application/json",
        status_code=status.HTTP_201_CREATED,
    )


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
