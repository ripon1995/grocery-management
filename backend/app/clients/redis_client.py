from redis.asyncio import Redis
from app.core.config import settings

redis_client: Redis | None = None

# TODO: use case in redis @asynccontextmanager
async def init_redis() -> None:
    global redis_client
    client = Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        decode_responses=True,
    )
    if redis_client:
        await redis_client.ping()
        redis_client = client


async def close_redis() -> None:
    global redis_client
    if redis_client:
        await redis_client.close()
