"""
Fake Gemini for the Phase 6 checks (GEMINI_PROVIDER=fake).

Acts like `genai.Client` for the one call the app makes
(`client.aio.models.generate_content`) without spending real quota:
- FAKE_GEMINI_LATENCY_S: how long a call takes
- FAKE_GEMINI_RPM: above this many calls a minute it returns 429 RESOURCE_EXHAUSTED (0 = no limit)
- FAKE_GEMINI_FAIL_RATE: fraction of calls that fail with 503 UNAVAILABLE

Every call is counted in Redis (`fake_gemini:calls`), and the per-minute counter
lives in Redis too, so the limit is shared by all API replicas like a real API key's quota.
"""

import asyncio
import hashlib
import json
import logging
import random
import re
import time
from dataclasses import dataclass
from typing import Any, List, get_args

from google.genai import errors
from redis.asyncio import Redis

from app.common.enums import MARKET_SHOPS, Seller
from app.core.config import settings

logger = logging.getLogger(__name__)

CALLS_KEY = 'fake_gemini:calls'
RPM_KEY_PREFIX = 'fake_gemini:rpm'

SHOP_DOMAINS = {
    Seller.SHWAPNO: 'shwapno.com',
    Seller.CHALDAL: 'chaldal.com',
    Seller.MEENA: 'meenabazaronline.com',
}


@dataclass
class FakeGenerateContentResponse:
    parsed: Any
    text: str


class FakeAsyncModels:
    def __init__(self, redis: Redis):
        self.redis = redis

    async def generate_content(self, *, model: str, contents: str, config: Any) -> FakeGenerateContentResponse:
        calls = await self.redis.incr(CALLS_KEY)
        logger.info(f"🤖 [FAKE GEMINI] call #{calls} (model={model})")

        await self.__check_rate_limit()
        await asyncio.sleep(settings.FAKE_GEMINI_LATENCY_S)

        if random.random() < settings.FAKE_GEMINI_FAIL_RATE:
            raise errors.ServerError(503, {'error': {
                'code': 503,
                'message': 'The model is overloaded. Please try again later. (fake)',
                'status': 'UNAVAILABLE',
            }})

        offers = self.__fake_offers(contents)
        offer_schema = get_args(config.response_schema)[0]  # response_schema is list[ShopOfferSchema]
        return FakeGenerateContentResponse(
            parsed=[offer_schema(**offer) for offer in offers],
            text=json.dumps(offers),
        )

    async def __check_rate_limit(self) -> None:
        if settings.FAKE_GEMINI_RPM <= 0:
            return
        key = f"{RPM_KEY_PREFIX}:{int(time.time() // 60)}"
        count = await self.redis.incr(key)
        if count == 1:
            await self.redis.expire(key, 120)
        if count > settings.FAKE_GEMINI_RPM:
            raise errors.ClientError(429, {'error': {
                'code': 429,
                'message': f'You exceeded your current quota ({settings.FAKE_GEMINI_RPM} requests per minute). (fake)',
                'status': 'RESOURCE_EXHAUSTED',
            }})

    @staticmethod
    def __fake_offers(contents: str) -> List[dict]:
        """Same item → same offers, so repeated explores (and later the cache) are comparable."""
        match = re.search(r'^Item: (.+)$', contents, re.MULTILINE)
        name = match.group(1).strip() if match else 'Unknown item'
        rng = random.Random(hashlib.sha256(name.encode()).hexdigest())

        base_price = rng.randint(50, 500)
        offers = []
        for shop in MARKET_SHOPS:
            if rng.random() < 0.2:  # sometimes a shop doesn't sell it
                continue
            slug = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')
            offers.append({
                'seller': shop.value,
                'product_name': name,
                'price': round(base_price * rng.uniform(0.9, 1.1)),
                'url': f"https://{SHOP_DOMAINS[shop]}/fake/{slug}",
            })
        return offers


class FakeAsyncClient:
    def __init__(self, redis: Redis):
        self.models = FakeAsyncModels(redis)

    async def aclose(self) -> None:
        pass


class FakeGeminiClient:
    def __init__(self, redis: Redis):
        self.aio = FakeAsyncClient(redis)
