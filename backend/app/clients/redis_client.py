import logging

from redis.asyncio import Redis
from app.core.config import settings

logger = logging.getLogger(__name__)

redis_client: Redis | None = None


async def init_redis() -> None:
    global redis_client
    logger.info(f"🧰 [REDIS] connecting to {settings.REDIS_HOST}:{settings.REDIS_PORT}")
    client = Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        decode_responses=True,
    )
    try:
        await client.ping()
    except Exception as e:
        logger.error(f"🧰 [REDIS] connection to {settings.REDIS_HOST}:{settings.REDIS_PORT} failed: {e!r}")
        await client.aclose()
        raise
    redis_client = client
    logger.info(f"🧰 [REDIS] connected to {settings.REDIS_HOST}:{settings.REDIS_PORT}")


async def close_redis() -> None:
    global redis_client
    if redis_client:
        await redis_client.aclose()
        redis_client = None
        logger.info("🧰 [REDIS] connection closed")


def get_redis() -> Redis:
    if redis_client is None:
        raise RuntimeError("Redis client is not initialized")
    return redis_client
