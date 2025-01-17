from typing import TYPE_CHECKING
import redis

from app.core.config import settings

if TYPE_CHECKING:
    from aioredis import Redis


async def get_redis() -> "Redis":
    redis_client: "Redis" = await redis.asyncio.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        encoding="utf-8",
        decode_responses=True,
    ).initialize()
    yield redis_client
