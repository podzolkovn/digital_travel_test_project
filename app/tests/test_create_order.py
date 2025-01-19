from httpx import AsyncClient, Response
from sqlalchemy import Result, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette.status import (
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_422_UNPROCESSABLE_ENTITY,
)

from app.domain.models import User, Order


async def test_success_create_order(
    login_user: tuple[AsyncClient, User],
    get_test_session: AsyncSession,
) -> None:
    """
    Test creating an order with valid data.
    This test verifies that an order is successfully created with valid input data,
    stored in the database, and the correct data is returned in the response.
    """

    async_client, user = login_user

    # Payload for creating the order
    payload: dict[str, str] = {
        "customer_name": "Test customer",
        "status": "PENDING",
        "products": [
            {
                "name": "product1",
                "price": 100,
                "quantity": 2,
            },
            {
                "name": "product2",
                "price": 150,
                "quantity": 5,
            },
        ],
    }

    # Step 1: Sending POST request to create an order
    response: Response = await async_client.post(
        url="/orders",
        json=payload,
    )

    # Step 2: Asserting the status code is HTTP_201_CREATED
    assert response.status_code == HTTP_201_CREATED

    # Step 3: Retrieving the created order from the database
    async with get_test_session as session:
        result_order: Result = await session.execute(
            select(Order)
            .filter_by(id=response.json()["id"])
            .options(selectinload(Order.products))
        )
        order: Order = result_order.scalars().first()

    # Step 4: Asserting the order was successfully created
    assert order.id is not None
    assert order.customer_name == response.json()["customer_name"]
    assert order.status.value == response.json()["status"]
    assert order.user_id == user.id
    assert len(payload["products"]) == len(order.products)

    # Step 5: Validating the product details
    for i in range(len(payload["products"])):
        assert response.json()["products"][i]["name"] == order.products[i].name
        assert response.json()["products"][i]["price"] == order.products[i].price
        assert response.json()["products"][i]["quantity"] == order.products[i].quantity


async def test_unauthorized_create_order(
    async_client: AsyncClient,
    get_test_session: AsyncSession,
) -> None:
    """
    Test creating an order without authentication.

    This test verifies that an unauthorized user cannot create an order,
    and the response returns a 401 Unauthorized status code.
    """

    # Payload for creating the order
    payload: dict[str, str] = {
        "customer_name": "Test customer",
        "status": "PENDING",
        "products": [
            {
                "name": "product1",
                "price": 100,
                "quantity": 2,
            },
            {
                "name": "product2",
                "price": 150,
                "quantity": 5,
            },
        ],
    }

    # Step 1: Sending POST request to create an order without authentication
    response: Response = await async_client.post(
        url="/orders",
        json=payload,
    )

    # Step 2: Asserting the status code is HTTP_401_UNAUTHORIZED
    assert response.status_code == HTTP_401_UNAUTHORIZED


async def test_bad_request_empty_data_create_order(
    login_user: tuple[AsyncClient, User],
    get_test_session: AsyncSession,
) -> None:
    """
    Test creating an order with missing required data.

    This test sends a POST request to create an order without providing
    required fields such as `customer_name`, `status`, and `products`.
    It verifies that the response returns a 422 Unprocessable Entity status code
    with appropriate error messages indicating the missing fields.
    """

    # Extracting the authenticated user and async client
    async_client, user = login_user

    # Step 1: Sending POST request to create an order with empty data
    response: Response = await async_client.post(
        url="/orders",
        json={},
    )

    # Step 2: Asserting the status code is HTTP_422_UNPROCESSABLE_ENTITY
    assert response.status_code == HTTP_422_UNPROCESSABLE_ENTITY

    # Step 3: Asserting the presence of specific missing field errors
    assert response.json()["detail"][0]["type"] == "missing"
    assert response.json()["detail"][0]["loc"] == ["body", "customer_name"]

    assert response.json()["detail"][1]["type"] == "missing"
    assert response.json()["detail"][1]["loc"] == ["body", "status"]

    assert response.json()["detail"][2]["type"] == "missing"
    assert response.json()["detail"][2]["loc"] == ["body", "products"]


async def test_bad_request_status_invalid_create_order(
    login_user: tuple[AsyncClient, User],
    get_test_session: AsyncSession,
) -> None:
    """
    Test creating an order with an invalid status.

    This test sends a POST request to create an order with an invalid status value,
    'asd', which is not one of the valid choices (PENDING, CONFIRMED, CANCELLED).
    It verifies that the response returns a 400 Bad Request status code with an
    appropriate error message indicating the invalid status.
    """

    # Extracting the authenticated user and async client
    async_client, user = login_user

    # Step 1: Sending POST request to create an order with invalid status
    payload: dict[str, str] = {
        "customer_name": "Test customer",
        "status": "asd",
        "products": [
            {
                "name": "product1",
                "price": 100,
                "quantity": 2,
            },
            {
                "name": "product2",
                "price": 150,
                "quantity": 5,
            },
        ],
    }

    response: Response = await async_client.post(
        url="/orders",
        json=payload,
    )

    # Step 2: Asserting the status code is HTTP_400_BAD_REQUEST
    assert response.status_code == HTTP_400_BAD_REQUEST

    # Step 3: Asserting the presence of invalid choice error with appropriate message
    assert (
        response.json()["detail"]["code"] == "invalid_choice"
    ), "asd is not a valid status. Available statuses are: PENDING, CONFIRMED, CANCELLED"


async def test_bad_request_product_price_invalid_create_order(
    login_user: tuple[AsyncClient, User],
    get_test_session: AsyncSession,
) -> None:
    """
    Test creating an order with a product that has an invalid price.

    This test sends a POST request to create an order with a product having a negative price,
    which should result in a 400 Bad Request response with an appropriate error message.
    """

    # Extracting the authenticated user and async client
    async_client, user = login_user

    # Step 1: Sending POST request to create an order with an invalid product price
    payload: dict[str, str] = {
        "customer_name": "Test customer",
        "status": "pending",
        "products": [
            {
                "name": "pending",
                "price": -123,
                "quantity": 2,
            },
        ],
    }

    response: Response = await async_client.post(
        url="/orders",
        json=payload,
    )

    # Step 2: Asserting the status code is HTTP_400_BAD_REQUEST
    assert response.status_code == HTTP_400_BAD_REQUEST

    # Step 3: Asserting the presence of negative or zero price error with appropriate message
    assert (
        response.json()["detail"]["code"] == "negative_or_zero"
    ), "Price must be greater than zero."


async def test_bad_request_product_quantity_invalid_create_order(
    login_user: tuple[AsyncClient, User],
    get_test_session: AsyncSession,
) -> None:
    """
    Test creating an order with a product that has an invalid quantity.

    This test sends a POST request to create an order with a product having a negative quantity,
    which should result in a 400 Bad Request response with an appropriate error message.
    """

    # Extracting the authenticated user and async client
    async_client, user = login_user

    # Step 1: Sending POST request to create an order with an invalid product quantity
    payload: dict[str, str] = {
        "customer_name": "Test customer",
        "status": "pending",
        "products": [
            {
                "name": "pending",
                "price": 120,
                "quantity": -1,
            },
        ],
    }

    response: Response = await async_client.post(
        url="/orders",
        json=payload,
    )

    # Step 2: Asserting the status code is HTTP_400_BAD_REQUEST
    assert response.status_code == HTTP_400_BAD_REQUEST

    # Step 3: Asserting the presence of negative or zero quantity error with appropriate message
    assert (
        response.json()["detail"]["code"] == "negative_or_zero"
    ), "Quantity must be greater than zero."


async def test_bad_request_product_price_empty_create_order(
    login_user: tuple[AsyncClient, User],
    get_test_session: AsyncSession,
) -> None:
    """
    Test creating an order with a product that has an empty price.

    This test sends a POST request to create an order with a product having an empty price,
    which should result in a 422 Unprocessable Entity response with an appropriate error message.
    """

    # Extracting the authenticated user and async client
    async_client, user = login_user

    # Step 1: Sending POST request to create an order with an empty product price
    payload: dict[str, str] = {
        "customer_name": "Test customer",
        "status": "pending",
        "products": [
            {
                "name": "pending",
                "price": "",
                "quantity": 12,
            },
        ],
    }

    response: Response = await async_client.post(
        url="/orders",
        json=payload,
    )

    # Step 2: Asserting the status code is HTTP_422_UNPROCESSABLE_ENTITY
    assert response.status_code == HTTP_422_UNPROCESSABLE_ENTITY

    # Step 3: Asserting the presence of float parsing error for empty price
    assert (
        response.json()["detail"][0]["type"] == "float_parsing"
    ), "Input should be a valid number, unable to parse string as a number"


async def test_bad_request_product_quantity_empty_create_order(
    login_user: tuple[AsyncClient, User],
    get_test_session: AsyncSession,
) -> None:
    """
    Test creating an order with a product that has an empty quantity.

    This test sends a POST request to create an order with a product having an empty quantity,
    which should result in a 422 Unprocessable Entity response with an appropriate error message.
    """

    # Extracting the authenticated user and async client
    async_client, user = login_user

    # Step 1: Sending POST request to create an order with an empty product quantity
    payload: dict[str, str] = {
        "customer_name": "Test customer",
        "status": "pending",
        "products": [
            {
                "name": "pending",
                "price": 123,
                "quantity": "",
            },
        ],
    }

    response: Response = await async_client.post(
        url="/orders",
        json=payload,
    )

    # Step 2: Asserting the status code is HTTP_422_UNPROCESSABLE_ENTITY
    assert response.status_code == HTTP_422_UNPROCESSABLE_ENTITY

    # Step 3: Asserting the presence of integer parsing error for empty quantity
    assert (
        response.json()["detail"][0]["type"] == "int_parsing"
    ), "Input should be a valid integer, unable to parse string as an integer"


async def test_bad_request_product_empty_create_order(
    login_user: tuple[AsyncClient, User],
    get_test_session: AsyncSession,
) -> None:
    """
    Test creating an order with an empty product list.

    This test sends a POST request to create an order with an empty list of products,
    which should result in a 400 Bad Request response with an appropriate error message.
    """

    # Extracting the authenticated user and async client
    async_client, user = login_user

    # Step 1: Sending POST request to create an order with an empty product list
    payload: dict[str, str] = {
        "customer_name": "Test customer",
        "status": "pending",
        "products": [],
    }

    response: Response = await async_client.post(
        url="/orders",
        json=payload,
    )

    # Step 2: Asserting the status code is HTTP_400_BAD_REQUEST
    assert response.status_code == HTTP_400_BAD_REQUEST

    # Step 3: Asserting the presence of null code error for empty products
    assert response.json()["detail"]["code"] == "null", "products must not be empty"
