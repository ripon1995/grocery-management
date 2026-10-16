"""
dependencies.py (feature scoped)

Feature-specific DI:
	•	feature-specific dependencies
"""

from aio_pika.abc import AbstractRobustChannel
from fastapi import Depends
from google import genai
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.gemini_client import get_gemini_client
from app.clients.rabbitmq_client import get_rabbitmq_channel
from app.clients.redis_client import get_redis
from app.db.session import get_db
from app.features.market.job_queue_service import MarketJobQueueService
from app.features.market.repository import MarketRepository
from app.features.market.service import MarketService
from app.services.redis_service import RedisService


def get_market_redis(redis: Redis = Depends(get_redis)) -> RedisService:
    return RedisService(redis)


def get_market_repository(db: AsyncSession = Depends(get_db)) -> MarketRepository:
    return MarketRepository(db)


def get_market_job_queue(
        rabbitmq_channel: AbstractRobustChannel = Depends(get_rabbitmq_channel),
        redis_service: RedisService = Depends(get_market_redis),
) -> MarketJobQueueService:
    return MarketJobQueueService(rabbitmq_channel, redis_service)


def get_market_service(
        repo: MarketRepository = Depends(get_market_repository),
        gemini: genai.Client = Depends(get_gemini_client),
        market_cache: RedisService = Depends(get_market_redis),
        job: MarketJobQueueService = Depends(get_market_job_queue),
) -> MarketService:
    return MarketService(repo, gemini, market_cache, job)
