from typing import Any, AsyncGenerator, Generator
import pytest_asyncio
from fakeredis.aioredis import FakeRedis
from httpx import AsyncClient, ASGITransport, Response
from sqlalchemy import select, Result
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from starlette.status import HTTP_201_CREATED, HTTP_200_OK

from app.domain.models import *  # noqa
from app.infrastructure.db import Base, get_async_session
from app.infrastructure.redis import get_redis
from app.main import app

engine = create_async_engine(
    "sqlite+aiosqlite:///./test.db",
    connect_args={"check_same_thread": False},
)

TestingSessionLocal = async_sessionmaker(
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
    bind=engine,
)


@pytest_asyncio.fixture(autouse=True)
async def init_db() -> AsyncGenerator[None, Any]:
    """Initialize the test database by creating and dropping all tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def override_get_async_session() -> Generator[AsyncSession, Any, None]:
    """Provide a database session for dependency overriding in tests."""
    async with TestingSessionLocal() as session:
        yield session


async def override_get_aioredis() -> Generator[FakeRedis, Any, None]:
    """Provide a FakeRedis instance for dependency overriding in tests."""
    r = FakeRedis()
    yield r
    await r.flushall()


app.dependency_overrides[get_async_session] = override_get_async_session
app.dependency_overrides[get_redis] = override_get_aioredis


@pytest_asyncio.fixture
async def get_test_session() -> Generator[AsyncSession, Any, None]:
    """Provide a database session for test functions."""
    async for session in override_get_async_session():
        yield session


@pytest_asyncio.fixture
async def get_test_redis() -> Generator[FakeRedis, Any, None]:
    """Provide a FakeRedis instance for test functions."""
    async for aioredis in override_get_aioredis():
        yield aioredis


@pytest_asyncio.fixture
async def async_client() -> Generator[AsyncClient, Any, None]:
    """Provide an asynchronous HTTP client for test functions."""
    async with AsyncClient(
        base_url="http://testserver",
        transport=ASGITransport(app=app),
    ) as ac:
        yield ac


@pytest_asyncio.fixture
def test_hash(request) -> str:
    """Generate a test hash based on the test name."""
    test_name = request.node.name
    return str(abs(hash(test_name)))


@pytest_asyncio.fixture(scope="function")
async def user_data(test_hash) -> dict[str, str]:
    """Provide a dictionary of user data for test functions"""
    return {
        "email": f"email_{test_hash}@gmail.com",
        "password": "password",
    }


@pytest_asyncio.fixture
async def create_user(
    async_client: AsyncClient,
    get_test_session: AsyncSession,
    user_data: dict[str, str],
) -> User:
    """Create a user in the test database."""
    response: Response = await async_client.post(
        url="/auth/register",
        json=user_data,
    )

    assert response.status_code == HTTP_201_CREATED

    async with get_test_session as session:
        result: Result = await session.execute(
            select(User).filter_by(id=response.json()["id"])
        )
        user: User = result.scalars().first()
        user.is_superuser = True
        await session.commit()

    return user


@pytest_asyncio.fixture
async def login_user(
    async_client: AsyncClient,
    create_user: User,
) -> tuple[AsyncClient, User]:
    """Login a user and return the async client and user instance."""
    user: User = create_user

    payload: dict[str, str] = {
        "grant_type": "password",
        "username": f"{user.email}",
        "password": "password",
    }

    response: Response = await async_client.post(
        url="/auth/login",
        data=payload,
    )

    assert response.status_code == HTTP_200_OK

    token: str = response.json().get("access_token")
    assert token is not None, "Access token not found in login response."

    async_client.headers.update({"Authorization": f"Bearer {token}"})

    return async_client, user
