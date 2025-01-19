from httpx import AsyncClient, Response
from sqlalchemy import Result, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_422_UNPROCESSABLE_ENTITY,
)

from app.domain.models import User, Order


async def test_success_update_order(
    login_user: tuple[AsyncClient, User],
    create_order: Order,
    get_test_session: AsyncSession,
) -> None:
    """
    Test successful update of an order with valid data.
    """

    # Step 1: Login as a user
    async_client, user = login_user

    # Step 2: Ensure user is a superuser
    assert user.is_superuser is True, "User is not a superuser."

    # Step 3: Create an order
    order: Order = await create_order(async_client)

    # Step 4: Send a PATCH request to update the order
    response: Response = await async_client.patch(
        url=f"/orders/{order.id}",
        json={
            "status": "CONFIRMED",
            "customer_name": "Test update order",
        },
    )

    # Step 5: Assert the response status is 200 OK
    assert response.status_code == HTTP_200_OK, response.json()

    # Step 6: Verify the order is updated in the database
    async with get_test_session as session:
        result_order: Result = await session.execute(
            select(Order).filter_by(id=order.id).options(selectinload(Order.products))
        )
        order: Order = result_order.scalars().first()

    # Step 7: Assert that the order status and customer name are updated
    assert (
        order.status.value == response.json()["status"]
    ), "Order status was not updated."
    assert (
        order.customer_name == response.json()["customer_name"]
    ), "Order customer name was not updated."


async def test_unauthorized_update_order(
    login_user: tuple[AsyncClient, User],
    create_order: Order,
    get_test_session: AsyncSession,
) -> None:
    """
    Test unauthorized update of an order.
    """

    # Step 1: Login as a user
    async_client, user = login_user

    # Step 2: Ensure user is a superuser
    assert user.is_superuser is True, "User is not a superuser."

    # Step 3: Create an order
    order: Order = await create_order(async_client)

    # Step 4: Remove the authorization header
    async_client.headers.pop("Authorization")

    # Step 5: Attempt to send a PATCH request to update the order
    response: Response = await async_client.patch(
        url=f"/orders/{order.id}",
        json={
            "status": "CONFIRMED",
            "customer_name": "Test update order",
        },
    )

    # Step 6: Assert the response status is 401 Unauthorized
    assert response.status_code == HTTP_401_UNAUTHORIZED, response.json()


async def test_forbidden_update_order(
    login_user: tuple[AsyncClient, User],
    create_order: Order,
    create_user: User,
    get_test_session: AsyncSession,
) -> None:
    """
    Test forbidden update of an order by a user who is not a superuser.
    """

    # Step 1: Login as a user
    async_client, user = login_user

    # Step 2: Ensure user is a superuser
    assert user.is_superuser is True, "User is not a superuser."

    # Step 3: Create an order
    order: Order = await create_order(async_client)

    # Step 4: Revoke superuser status and change email
    async with get_test_session as session:
        result: Result = await session.execute(select(User).filter_by(id=user.id))
        user: User = result.scalars().first()
        user.is_superuser = False
        user.email = "change_email@gmail.com"
        await session.commit()

    # Step 5: Create another user to assign as the new user for the order
    user_second: User = create_user

    # Step 6: Attempt to update the order with a non-superuser
    response: Response = await async_client.patch(
        url=f"/orders/{order.id}",
        json={
            "user_id": user_second.id,
        },
    )

    # Step 7: Assert the response status is 403 Forbidden
    assert response.status_code == HTTP_403_FORBIDDEN, response.json()


async def test_bad_request_status_update_order(
    login_user: tuple[AsyncClient, User],
    create_order: Order,
    create_user: User,
    get_test_session: AsyncSession,
) -> None:
    """
    Test that an attempt to update an order with an invalid status results in a bad request.
    """

    # Step 1: Login as a user
    async_client, user = login_user

    # Step 2: Ensure user is a superuser
    assert user.is_superuser is True, "User is not a superuser."

    # Step 3: Create an order
    order: Order = await create_order(async_client)

    # Step 4: Attempt to update the order with an invalid status
    response: Response = await async_client.patch(
        url=f"/orders/{order.id}",
        json={
            "status": "INVALID_STATUS",
        },
    )

    # Step 5: Assert the response status is 400 Bad Request
    assert response.status_code == HTTP_400_BAD_REQUEST, response.json()

    # Step 6: Assert the appropriate error code is returned
    assert response.json()["detail"]["code"] == "invalid_choice"


async def test_bad_request_user_id_update_order(
    login_user: tuple[AsyncClient, User],
    create_order: Order,
    create_user: User,
    get_test_session: AsyncSession,
) -> None:
    """
    Test that an attempt to update an order with a non-existent user ID results in a bad request.
    """

    # Step 1: Login as a user
    async_client, user = login_user

    # Step 2: Ensure user is a superuser
    assert user.is_superuser is True, "User is not a superuser."

    # Step 3: Create an order
    order: Order = await create_order(async_client)

    # Step 4: Attempt to update the order with a non-existent user ID
    response: Response = await async_client.patch(
        url=f"/orders/{order.id}",
        json={
            "user_id": 123123123,
        },
    )

    # Step 5: Assert the response status is 400 Bad Request
    assert response.status_code == HTTP_400_BAD_REQUEST, response.json()

    # Step 6: Assert the appropriate error code is returned
    assert response.json()["detail"]["code"] == "does_not_exist"


async def test_bad_request_empty_data_update_order(
    login_user: tuple[AsyncClient, User],
    create_order: Order,
    create_user: User,
    get_test_session: AsyncSession,
) -> None:
    """
    Test that attempting to update an order with empty data results in a bad request.
    """

    # Step 1: Login as a user
    async_client, user = login_user

    # Step 2: Ensure user is a superuser
    assert user.is_superuser is True, "User is not a superuser."

    # Step 3: Create an order
    order: Order = await create_order(async_client)

    # Step 4: Attempt to update the order with empty data
    response: Response = await async_client.patch(
        url=f"/orders/{order.id}",
        json={},
    )

    # Step 5: Assert the response status is 400 Bad Request
    assert response.status_code == HTTP_400_BAD_REQUEST, response.json()


async def test_bad_request_empty_status_update_order(
    login_user: tuple[AsyncClient, User],
    create_order: Order,
    create_user: User,
    get_test_session: AsyncSession,
) -> None:
    """
    Test that attempting to update an order with an empty user_id results in an unprocessable entity.
    """

    # Step 1: Login as a user
    async_client, user = login_user

    # Step 2: Ensure user is a superuser
    assert user.is_superuser is True, "User is not a superuser."

    # Step 3: Create an order
    order: Order = await create_order(async_client)

    # Step 4: Attempt to update the order with an empty user_id
    response: Response = await async_client.patch(
        url=f"/orders/{order.id}",
        json={
            "user_id": "",
        },
    )

    # Step 5: Assert the response status is 422 Unprocessable Entity
    assert response.status_code == HTTP_422_UNPROCESSABLE_ENTITY, response.json()

    # Step 6: Assert the response contains the correct error type
    assert (
        response.json()["detail"][0]["type"] == "int_parsing"
    ), "Input should be a valid integer, unable to parse string as an integer"


async def test_not_found_update_order(
    login_user: tuple[AsyncClient, User],
    create_order: Order,
    create_user: User,
    get_test_session: AsyncSession,
) -> None:
    """
    Test that updating an order with a non-existent order ID results in a not found error.
    """

    # Step 1: Login as a user
    async_client, user = login_user

    # Step 2: Ensure user is a superuser
    assert user.is_superuser is True, "User is not a superuser."

    # Step 3: Attempt to update a non-existent order
    response: Response = await async_client.patch(
        url=f"/orders/123123123123",
        json={
            "status": "CONFIRMED",
            "customer_name": "Test update order",
        },
    )

    # Step 4: Assert the response status is 404 Not Found
    assert response.status_code == HTTP_404_NOT_FOUND, response.json()
