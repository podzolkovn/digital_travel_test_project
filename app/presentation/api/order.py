from starlette import status

from fastapi import APIRouter, Depends, Response
from starlette.responses import JSONResponse

from app.application.managers.order import OrderManager
from app.domain.dependencies.order import get_order_db
from app.domain.models.auth import User
from app.domain.models.order import StatusEnum
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
    summary="Create a new order",
    description=f"""The endpoint is responsible for creating a new order.

        Options:
        {''.join([f"{key} - {value}, " for key, value in StatusEnum.__members__.items()])}
        """,
    dependencies=[Depends(current_user)],
    status_code=status.HTTP_201_CREATED,
    response_description="Successful. The order has been created.",
    response_model=OrderRead,
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "description": "Bad Request. Return the errors list for each field that is invalid.",
        },
    },
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
    path="/{order_id}",
    summary="Get detail of order",
    description=f"""This endpoint retrieves detailed information about an order by id.""",
    dependencies=[Depends(current_user)],
    status_code=status.HTTP_200_OK,
    response_description="Successful. The get order.",
    response_model=OrderRead,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "Resource not found. The requested resource does not exist or is unavailable."
            " Please check the URL or request parameters and try again.",
        },
    },
)
async def get_order(
    order_id: int,
    user: UserRead = Depends(current_user),
    order_repository: OrdersRepository = Depends(get_order_db),
) -> JSONResponse:
    order_manager: OrderManager = OrderManager(order_repository=order_repository)
    order_data: JSONResponse = await order_manager.get_details(
        order_id,
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
