from typing import Any, AsyncGenerator, Generator
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.domain.models import *  # noqa
from app.infrastructure.db import Base, get_async_session
from app.main import app

engine = create_async_engine(
    "sqlite+aiosqlite:///./test.db",
    connect_args={"check_same_thread": False},
    echo=True,
)

TestingSessionLocal = async_sessionmaker(
    expire_on_commit=False, autocommit=False, autoflush=False, bind=engine
)


@pytest_asyncio.fixture(autouse=True)
async def init_db() -> AsyncGenerator[None, Any]:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def override_get_async_session() -> Generator[AsyncSession, Any, None]:
    async with TestingSessionLocal() as session:
        yield session


app.dependency_overrides[get_async_session] = override_get_async_session


@pytest_asyncio.fixture
async def get_test_session() -> Generator[AsyncSession, Any, None]:
    async for session in override_get_async_session():
        yield session


@pytest_asyncio.fixture
async def async_client() -> Generator[AsyncClient, Any, None]:
    async with AsyncClient(
        base_url="http://testserver", transport=ASGITransport(app=app)
    ) as ac:
        yield ac
