from starlette.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
)

from fastapi import APIRouter, Depends, Query
from starlette.responses import JSONResponse

from app.application.managers.order import OrderManager
from app.application.managers.user import UserManager
from app.domain.dependencies.order import get_order_db
from app.domain.dependencies.user import get_user_manager
from app.domain.models.order import StatusEnum
from app.domain.repositories.orders import OrdersRepository
from app.domain.schemas.order import OrderWrite, OrderRead, OrderUpdate
from app.domain.schemas.user import UserRead
from app.presentation.api.fastapi_users import current_user, current_super_user

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
    status_code=HTTP_201_CREATED,
    response_description="Successful. The order has been created.",
    response_model=OrderRead,
    responses={
        HTTP_400_BAD_REQUEST: {
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
    status_code=HTTP_200_OK,
    response_description="Successful. The get order.",
    response_model=OrderRead,
    responses={
        HTTP_404_NOT_FOUND: {
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


@router.delete(
    path="/{order_id}",
    summary="Delete order",
    description=f"""This endpoint deleted order by id.""",
    dependencies=[Depends(current_super_user)],
    status_code=HTTP_200_OK,
    response_description="Successful. The delete order.",
    response_model=OrderRead,
    responses={
        HTTP_401_UNAUTHORIZED: {
            "description": "Unauthorized access",
        },
        HTTP_403_FORBIDDEN: {
            "description": "Forbidden access",
        },
        HTTP_404_NOT_FOUND: {
            "description": "Resource not found. The requested resource does not exist or is unavailable."
            " Please check the URL or request parameters and try again.",
        },
    },
)
async def delete_order(
    order_id: int,
    user: UserRead = Depends(current_super_user),
    order_repository: OrdersRepository = Depends(get_order_db),
) -> JSONResponse:
    order_manager: OrderManager = OrderManager(order_repository=order_repository)
    order_data: JSONResponse = await order_manager.soft_delete(
        order_id,
        user=user,
    )
    return order_data


@router.get(
    path="",
    summary="Get list orders",
    description=f"""This endpoint get list orders.
        Options:
            {''.join([f"{key} - {value}, " for key, value in StatusEnum.__members__.items()])}
        """,
    dependencies=[Depends(current_user)],
    status_code=HTTP_200_OK,
    response_description="Successful. The get list orders.",
    response_model=list[OrderRead],
    responses={
        HTTP_400_BAD_REQUEST: {
            "description": "Bad Request. Return the errors list for each field that is invalid.",
        },
        HTTP_401_UNAUTHORIZED: {
            "description": "Unauthorized access",
        },
    },
)
async def get_orders(
    status: str | None = Query(
        default=None,
        description="Filter by order status",
    ),
    min_price: float | None = Query(
        default=None,
        description="Filter by minimum price",
    ),
    max_price: float | None = Query(
        default=None,
        description="Filter by maximum price",
    ),
    user: UserRead = Depends(current_user),
    order_repository: OrdersRepository = Depends(get_order_db),
) -> JSONResponse:
    order_manager: OrderManager = OrderManager(order_repository=order_repository)
    orders_data: JSONResponse = await order_manager.filter_orders(
        user=user,
        filters={
            "status": status,
            "min_price": min_price,
            "max_price": max_price,
        },
    )
    return orders_data


@router.patch(
    path="/{order_id}",
    summary="Update order",
    description=f"""This endpoint responsibility for updated order.
        Options:
            {''.join([f"{key} - {value}, " for key, value in StatusEnum.__members__.items()])}
        """,
    dependencies=[Depends(current_user)],
    status_code=HTTP_200_OK,
    response_description="Successful. The updated order.",
    response_model=OrderRead,
    responses={
        HTTP_400_BAD_REQUEST: {
            "description": "Bad Request. Return the errors list for each field that is invalid.",
        },
        HTTP_401_UNAUTHORIZED: {
            "description": "Unauthorized access",
        },
        HTTP_404_NOT_FOUND: {
            "description": "Resource not found. The requested resource does not exist or is unavailable."
            " Please check the URL or request parameters and try again.",
        },
    },
)
async def update_order(
    order_id: int,
    data: OrderUpdate,
    user: UserRead = Depends(current_user),
    order_repository: OrdersRepository = Depends(get_order_db),
    user_manager: UserManager = Depends(get_user_manager),
) -> JSONResponse:
    order_manager: OrderManager = OrderManager(order_repository=order_repository)
    orders_data: JSONResponse = await order_manager.on_after_update(
        pk=order_id,
        user=user,
        data=data.dict(exclude_unset=True),
        user_manager=user_manager,
    )
    return orders_data
