from httpx import AsyncClient, Response
from sqlalchemy import Result, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette.status import (
    HTTP_200_OK,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
)

from app.domain.models import User, Order


async def test_success_delete_order(
    login_user: tuple[AsyncClient, User],
    create_order: Order,
    get_test_session: AsyncSession,
) -> None:
    """
    Test successful deletion of an order.
    """

    # Step 1: Login as a user
    async_client, user = login_user

    # Step 2: Create an order
    order: Order = await create_order(async_client)

    # Step 3: Send a DELETE request to delete the order
    response: Response = await async_client.delete(url=f"/orders/{order.id}")

    # Step 4: Assert that the response status code is 200 OK
    assert response.status_code == HTTP_200_OK, response.json()

    # Step 5: Verify that the order has been soft deleted in the database
    async with get_test_session as session:
        result_order: Result = await session.execute(
            select(Order).filter_by(id=order.id).options(selectinload(Order.products))
        )
        order: Order = result_order.scalars().first()

    # Step 6: Assert that the order's `is_deleted` field is True
    assert order.is_deleted is True, "Order was not soft deleted."


async def test_unauthorized_delete_order(
    login_user: tuple[AsyncClient, User],
    create_order: Order,
    get_test_session: AsyncSession,
    async_client: AsyncClient,
) -> None:
    """
    Test unauthorized deletion of an order without providing an authorization token.
    """

    # Step 1: Login as a user
    async_client, user = login_user

    # Step 2: Create an order
    order: Order = await create_order(async_client)

    # Step 3: Remove the Authorization header from the async client
    async_client.headers.pop("Authorization")

    # Step 4: Attempt to delete the order
    response: Response = await async_client.delete(url=f"/orders/{order.id}")

    # Step 5: Assert that the response status code is 401 Unauthorized
    assert response.status_code == HTTP_401_UNAUTHORIZED, response.json()


async def test_forbidden_delete_order(
    login_user: tuple[AsyncClient, User],
    create_order: Order,
    get_test_session: AsyncSession,
    async_client: AsyncClient,
) -> None:
    """
    Test forbidden deletion of an order by a non-superuser user.
    """

    # Step 1: Login as a user
    async_client, user = login_user

    # Step 2: Create an order
    order: Order = await create_order(async_client)

    # Step 3: Set the user as non-superuser
    async with get_test_session as session:
        result: Result = await session.execute(select(User).filter_by(id=user.id))
        user: User = result.scalars().first()
        user.is_superuser = False
        await session.commit()

    # Step 4: Attempt to delete the order
    response: Response = await async_client.delete(url=f"/orders/{order.id}")

    # Step 5: Assert that the response status code is 403 Forbidden
    assert response.status_code == HTTP_403_FORBIDDEN, response.json()


async def test_not_found_delete_order(
    login_user: tuple[AsyncClient, User],
    create_order: Order,
    get_test_session: AsyncSession,
    async_client: AsyncClient,
) -> None:
    """
    Test deletion of a non-existent order returns a 404 Not Found status.
    """

    # Step 1: Login as a user
    async_client, user = login_user

    # Step 2: Attempt to delete a non-existent order
    response: Response = await async_client.delete(url=f"/orders/23432423432423")

    # Step 3: Assert that the response status code is 404 Not Found
    assert response.status_code == HTTP_404_NOT_FOUND, response.json()
