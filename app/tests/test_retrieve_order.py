from httpx import AsyncClient
from sqlalchemy import select, Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette.status import HTTP_200_OK, HTTP_401_UNAUTHORIZED, HTTP_404_NOT_FOUND

from app.domain.models import User, Order


async def test_success_retrieve_order(
    login_user: tuple[AsyncClient, User],
    create_order: Order,
    create_user: User,
    get_test_session: AsyncSession,
) -> None:
    """
    Test successful retrieval of a specific order and its associated products.
    """

    # Step 1: Login as a user
    client, user = login_user

    # Step 2: Create multiple orders
    order_first: Order = await create_order(client)
    await create_order(client, customer_name="Test customer name", status="CONFIRMED")
    await create_order(client, customer_name="Test customer name 3", status="CANCELLED")

    # Step 3: Assert user is a superuser
    assert user.is_superuser is True, "User is not a superuser."

    # Step 4: Retrieve a specific order by ID
    response = await client.get(f"/orders/{order_first.id}")
    assert response.status_code == HTTP_200_OK

    # Step 5: Validate order and products using the database session
    async with get_test_session as session:
        result: Result = await session.execute(
            select(Order)
            .filter_by(id=order_first.id)
            .options(selectinload(Order.products))
        )
        order: Order = result.scalar()

    # Step 6: Assert order details match the response
    assert order.id == response.json()["id"]
    assert order.customer_name == response.json()["customer_name"]
    assert order.status.value == response.json()["status"]
    assert order.total_price == response.json()["total_price"]

    # Step 7: Assert product details match the response
    for i in range(len(order.products)):
        assert order.products[i].id == response.json()["products"][i]["id"]
        assert order.products[i].name == response.json()["products"][i]["name"]
        assert order.products[i].price == response.json()["products"][i]["price"]
        assert order.products[i].quantity == response.json()["products"][i]["quantity"]


async def test_unauthorized_retrieve_order(
    login_user: tuple[AsyncClient, User],
    create_order: Order,
    create_user: User,
    get_test_session: AsyncSession,
) -> None:
    """
    Test unauthorized access when attempting to retrieve an order.
    """

    # Step 1: Login as a user
    client, user = login_user

    # Step 2: Create an order
    order_first: Order = await create_order(client)

    # Step 3: Assert user is a superuser
    assert user.is_superuser is True, "User is not a superuser."

    # Step 4: Remove authorization token
    client.headers.pop("Authorization")

    # Step 5: Attempt to retrieve the order
    response = await client.get(f"/orders/{order_first.id}")
    assert response.status_code == HTTP_401_UNAUTHORIZED


async def test_not_found_retrieve_order(
    login_user: tuple[AsyncClient, User],
    create_order: Order,
    create_user: User,
    get_test_session: AsyncSession,
) -> None:
    """
    Test retrieving a non-existent order.
    """

    # Step 1: Login as a user
    client, user = login_user

    # Step 2: Assert user is a superuser
    assert user.is_superuser is True, "User is not a superuser."

    # Step 3: Attempt to retrieve a non-existent order
    response = await client.get(f"/orders/23786542378")

    # Step 4: Assert that the response status is HTTP 404 NOT FOUND
    assert response.status_code == HTTP_404_NOT_FOUND

