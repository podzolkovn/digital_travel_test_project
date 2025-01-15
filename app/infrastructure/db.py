from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, AsyncEngine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from typing_extensions import AsyncGenerator

from app.core.config import settings


class Base(DeclarativeBase):
    pass


# Create an asynchronous engine for the database connection
engine: AsyncEngine = create_async_engine(
    url=settings.DB_URL
)

# Create an asynchronous session maker
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function to provide an asynchronous SQLAlchemy session.
    Ensures proper management of session lifecycle.
    """
    async with async_session_maker() as session:
        yield session
