"""
dependencies.py (feature scoped)

Feature-specific DI:
	•	feature-specific dependencies
"""

from fastapi import Depends
from google import genai
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.gemini_client import get_gemini_client
from app.clients.redis_client import get_redis
from app.db.session import get_db
from app.features.market.repository import MarketRepository
from app.features.market.service import MarketService
from app.services.redis_service import RedisService


def get_market_redis(redis: Redis = Depends(get_redis)) -> RedisService:
    return RedisService(redis)


def get_market_repository(db: AsyncSession = Depends(get_db)) -> MarketRepository:
    return MarketRepository(db)


def get_market_service(
        repo: MarketRepository = Depends(get_market_repository),
        gemini: genai.Client = Depends(get_gemini_client),
        market_cache: RedisService = Depends(get_market_redis),
) -> MarketService:
    return MarketService(repo, gemini, market_cache)
