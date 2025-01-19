from httpx import AsyncClient, Response
from sqlalchemy import select, Result
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_201_CREATED, HTTP_422_UNPROCESSABLE_ENTITY

from app.domain.models import User


async def test_success_register(
    async_client: AsyncClient,
    get_test_session: AsyncSession,
) -> None:
    """
    Test the successful registration functionality by verifying the created user
    exists in the database and the response matches the input data.
    """
    # Step 1: Send a POST request to the registration endpoint with user details.
    response: Response = await async_client.post(
        url="/auth/register",
        json={
            "email": "email@gmail.com",
            "password": "password",
        },
    )

    # Step 2: Assert that the response status code is 201 (Created).
    assert response.status_code == HTTP_201_CREATED

    # Step 3: Verify the user exists in the database.
    async with get_test_session as session:
        user: Result = await session.execute(
            select(User).filter_by(email="email@gmail.com")
        )
        user: User = user.scalars().first()

        # Step 4: Assert that the user is not None (successfully created).
        assert user is not None

        # Step 5: Assert that the user's email matches the one in the response.
        assert user.email == response.json()["email"]


async def test_success_check_is_not_superuser_register(
    async_client: AsyncClient,
    get_test_session: AsyncSession,
) -> None:
    """
    Test registration to ensure that the `is_superuser` flag is not set to True
    even if explicitly provided in the registration payload.
    """
    # Step 1: Send a POST request to the registration endpoint with user details
    # and explicitly set "is_superuser" to True.
    response: Response = await async_client.post(
        url="/auth/register",
        json={
            "email": "email@gmail.com",
            "password": "password",
            "is_superuser": True,
        },
    )

    # Step 2: Assert that the response status code is 201 (Created).
    assert response.status_code == HTTP_201_CREATED

    # Step 3: Query the database to fetch the user with the provided email.
    async with get_test_session as session:
        user: Result = await session.execute(
            select(User).filter_by(email="email@gmail.com")
        )
        user: User = user.scalars().first()

        # Step 4: Assert that the user exists in the database.
        assert user is not None

        # Step 5: Assert that the email in the database matches the one in the response.
        assert user.email == response.json()["email"]

        # Step 6: Assert that the `is_superuser` flag is set to False
        # in both the database and the response.
        assert user.is_superuser == response.json()["is_superuser"] is False


async def test_bad_request_email_register(
    async_client: AsyncClient,
    get_test_session: AsyncSession,
) -> None:
    """
    Test registration with an invalid email to ensure the API returns a 422 error
    and provides appropriate validation error details.
    """
    # Step 1: Send a POST request to the registration endpoint with an invalid email format.
    response: Response = await async_client.post(
        url="/auth/register",
        json={
            "email": "email",  # Invalid email without "@" or domain
            "password": "password",
        },
    )

    # Step 2: Assert that the response status code is 422 (Unprocessable Entity).
    assert response.status_code == HTTP_422_UNPROCESSABLE_ENTITY

    # Step 3: Verify that the response contains validation error details
    # indicating the email is not in a valid format.
    assert (
        response.json()["detail"][0]["type"] == "value_error"
    ), "value is not a valid email address: An email address must have an @-sign"


async def test_bad_request_empty_data_register(
    async_client: AsyncClient,
    get_test_session: AsyncSession,
) -> None:
    """
    Test registration with an empty payload to ensure the API returns a 422 error
    and provides appropriate error details indicating required fields are missing.
    """
    # Step 1: Send a POST request to the registration endpoint with an empty JSON payload.
    response: Response = await async_client.post(
        url="/auth/register",
        json={},  # Empty payload
    )

    # Step 2: Assert that the response status code is 422 (Unprocessable Entity).
    assert response.status_code == HTTP_422_UNPROCESSABLE_ENTITY

    # Step 3: Verify that the response contains error details indicating
    # missing fields, with the error type set to "missing."
    assert response.json()["detail"][0]["type"] == "missing", "Field required"

