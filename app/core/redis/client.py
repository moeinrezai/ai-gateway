from collections.abc import AsyncGenerator

import redis.asyncio as aioredis

from app.core.config import settings

redis_client = aioredis.from_url(
    url=settings.redis_url,
    encoding="utf-8",
    decode_responses=True,
    health_check_interval=30,
)


async def get_redis() -> AsyncGenerator[aioredis.Redis, None]:
    yield redis_client