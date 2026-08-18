from redis.asyncio import Redis
from app.core.config import settings

redis_client: Redis | None = None


async def init_redis() -> None:
    global redis_client
    client = Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        decode_responses=True,
    )
    await client.ping()
    redis_client = client


async def close_redis() -> None:
    global redis_client
    if redis_client:
        await redis_client.close()


def get_redis() -> Redis:
    if redis_client is None:
        raise RuntimeError("Redis client is not initialized")
    return redis_client
