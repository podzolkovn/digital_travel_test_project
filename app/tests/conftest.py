import pytest
from app.core.config import settings
from app.infrastructure.db import engine, Base
from app.domain.models.auth import User


@pytest.fixture(autouse=True)
async def setup_db() -> None:
    """
    This is a pytest fixture that sets up and tears down the database schema before and after each test,
    ensuring the environment is reset to a clean state.
    """
    assert settings.MODE == "TEST"

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
