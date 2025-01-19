from httpx import AsyncClient
from sqlalchemy import select, Result, ScalarResult, Select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED

from app.domain.models import User, Order


async def test_success_get_all_orders(
    login_user: tuple[AsyncClient, User],
    create_order: Order,
    create_user: User,
    get_test_session: AsyncSession,
) -> None:
    """
    Test retrieving all orders successfully.
    """

    # Step 1: Login as a user
    client, user = login_user

    # Step 2: Create multiple orders
    await create_order(client)
    await create_order(client, customer_name="Test customer name", status="CONFIRMED")
    await create_order(client, customer_name="Test customer name 3", status="CANCELLED")

    # Step 3: Ensure user is a superuser
    assert user.is_superuser is True, "User is not a superuser."

    # Step 4: Retrieve all orders
    response = await client.get("/orders")
    assert response.status_code == HTTP_200_OK

    # Step 5: Verify the number of orders retrieved matches the database
    async with get_test_session as session:
        result: Result = await session.execute(select(Order))
        orders: list[Order] = result.scalars().all()

    assert len(response.json()) == len(orders)


async def test_success_filter_by_status_orders(
    login_user: tuple[AsyncClient, User],
    create_order: Order,
    create_user: User,
    get_test_session: AsyncSession,
) -> None:
    """
    Test filtering orders by status successfully.
    """

    # Step 1: Login as a user
    client, user = login_user

    # Step 2: Create multiple orders with different statuses
    await create_order(client)
    await create_order(client, customer_name="Test customer name", status="CONFIRMED")
    await create_order(client, customer_name="Test customer name 3", status="CANCELLED")

    # Step 3: Ensure user is a superuser
    assert user.is_superuser is True, "User is not a superuser."

    # Step 4: Filter orders by status 'CONFIRMED'
    response = await client.get("/orders?status=CONFIRMED")
    assert response.status_code == HTTP_200_OK

    # Step 5: Verify the filtered orders match the status
    async with get_test_session as session:
        result: Result = await session.execute(
            select(Order).filter(Order.status == "CONFIRMED")
        )
        orders: list[Order] = result.scalars().all()

    assert len(response.json()) == len(orders)
    assert response.json()[0]["status"] == orders[0].status.value


async def test_success_filter_by_price_orders(
    login_user: tuple[AsyncClient, User],
    create_order: Order,
    create_user: User,
    get_test_session: AsyncSession,
) -> None:
    """
    Test filtering orders by total price successfully.
    """

    # Step 1: Login as a user
    client, user = login_user

    # Step 2: Create multiple orders with different prices
    order_first: Order = await create_order(client)
    order_second: Order = await create_order(
        client, customer_name="Test customer name", status="CONFIRMED"
    )
    await create_order(client, customer_name="Test customer name 3", status="CANCELLED")

    # Step 3: Update the total price of created orders in the database
    async with get_test_session as session:
        result: Result = await session.execute(
            select(Order).filter(Order.id == order_first.id)
        )
        order_first_update: Order = result.scalar()
        order_first_update.total_price = 100
        await session.commit()

        result: Result = await session.execute(
            select(Order).filter(Order.id == order_second.id)
        )
        order_second_update: Order = result.scalar()
        order_second_update.total_price = 500
        await session.commit()

    # Step 4: Ensure user is a superuser
    assert user.is_superuser is True, "User is not a superuser."

    # Step 5: Filter orders by total price range
    max_price: int = 2000
    min_price: int = 400
    response = await client.get(f"/orders?min_price={min_price}&max_price={max_price}")

    assert response.status_code == HTTP_200_OK, response.json()

    # Step 6: Verify the filtered orders match the price range
    async with get_test_session as session:
        stmt: Select = select(Order).where(
            Order.total_price >= min_price, Order.total_price <= max_price
        )
        result: ScalarResult[Order] = await session.scalars(stmt)
        orders = result.all()

    assert len(response.json()) == len(orders), response.json()


async def test_bad_request_invalid_status_in_filter(
    login_user: tuple[AsyncClient, User],
    create_order: Order,
    create_user: User,
    get_test_session: AsyncSession,
) -> None:
    """
    Test filtering orders by an invalid status, expecting a bad request response.
    """

    # Step 1: Login as a user
    client, user = login_user

    # Step 2: Create multiple orders with different statuses
    await create_order(client)
    await create_order(client, customer_name="Test customer name", status="CONFIRMED")
    await create_order(client, customer_name="Test customer name 3", status="CANCELLED")

    # Step 3: Filter orders by an invalid status
    response = await client.get(f"/orders?status=INVALID_STATUS")

    # Step 4: Assert bad request response
    assert response.status_code == HTTP_400_BAD_REQUEST, response.json()
    assert (
        response.json()["detail"]["code"] == "invalid_choice"
    ), "Invalid status code not found in response"


async def test_bad_request_invalid_price_in_filter(
    login_user: tuple[AsyncClient, User],
    create_order: Order,
    create_user: User,
    get_test_session: AsyncSession,
) -> None:
    """
    Test filtering orders by an invalid price range, expecting a bad request response.
    """

    # Step 1: Login as a user
    client, user = login_user

    # Step 2: Create multiple orders with different statuses
    await create_order(client)
    await create_order(client, customer_name="Test customer name", status="CONFIRMED")
    await create_order(client, customer_name="Test customer name 3", status="CANCELLED")

    # Step 3: Use an invalid price range
    min_price: int = 2000
    max_price: int = 400
    response = await client.get(f"/orders?min_price={min_price}&max_price={max_price}")

    # Step 4: Assert bad request response
    assert response.status_code == HTTP_400_BAD_REQUEST, response.json()
    assert (
        response.json()["detail"]["code"] == "invalid_price_range"
    ), "Invalid price range code not found in response"


async def test_unauthorized_invalid_price_in_filter(
    login_user: tuple[AsyncClient, User],
    create_order: Order,
    create_user: User,
    get_test_session: AsyncSession,
) -> None:
    """
    Test unauthorized access when filtering orders by invalid price range.
    """

    # Step 1: Login as a user
    client, user = login_user

    # Step 2: Create multiple orders with different statuses
    await create_order(client)
    await create_order(client, customer_name="Test customer name", status="CONFIRMED")
    await create_order(client, customer_name="Test customer name 3", status="CANCELLED")

    # Step 3: Remove the Authorization header to simulate an unauthorized request
    client.headers.pop("Authorization")

    # Step 4: Attempt to filter orders with invalid price range
    response = await client.get(f"/orders")

    # Step 5: Assert unauthorized response
    assert response.status_code == HTTP_401_UNAUTHORIZED, response.json()
