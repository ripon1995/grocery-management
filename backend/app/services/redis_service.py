from typing import Any
from redis.asyncio import Redis
import json


class RedisService:
    def __init__(self, redis_client: Redis):

        self.redis = redis_client

    async def get(self, key: str) -> Any:
        value = await self.redis.get(key)
        return json.loads(value) if value else None

    async def set(self, key: str, value: Any, ttl: int = 300) -> None:
        await self.redis.setex(key, ttl, json.dumps(value))

    async def delete(self, key: str) -> None:
        await self.redis.delete(key)
