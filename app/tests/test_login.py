from httpx import AsyncClient, Response
from sqlalchemy import Result, select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_200_OK

from app.domain.models import User, AccessToken


async def test_success_login(
    async_client: AsyncClient, create_user: User, get_test_session: AsyncSession
) -> None:
    """
    Test the successful login functionality by verifying the returned access token
    and its presence in the database.
    """
    # Step 1: Create a test user.
    user: User = create_user

    # Step 2: Prepare the payload for the login request.
    payload: dict[str, str] = {
        "grant_type": "password",
        "username": f"{user.email}",
        "password": "password",
    }

    # Step 3: Send a POST request to the login endpoint with the payload.
    response: Response = await async_client.post(
        url="/auth/login",
        data=payload,
    )

    # Step 4: Assert that the response status code is 200 (OK).
    assert response.status_code == HTTP_200_OK

    # Step 5: Verify the access token from the response exists in the database.
    async with get_test_session as session:
        result: Result = await session.execute(
            select(AccessToken).filter_by(token=response.json()["access_token"])
        )
        access_token: AccessToken = result.scalars().first()

    # Step 6: Assert that the access token in the response matches the one in the database.
    assert (
        response.json()["access_token"] == access_token.token
    ), "Access token not found in login response."
