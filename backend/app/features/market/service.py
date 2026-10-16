"""
service.py — Business logic layer
"""

import logging
from typing import List
from uuid import UUID

from google import genai
from google.genai import errors, types

from app.core.config import settings
from app.core.exceptions import (
    GeminiException,
    GeminiRateLimitException,
    GeminiUnavailableException,
)
from app.features.grocery.models import Grocery
from app.services.redis_service import RedisService
from .repository import MarketRepository
from .schemas.response_schemas import (
    MarketExploreResponseSchema,
    GroceryExploreResultSchema,
    ShopOfferSchema,
)

logger = logging.getLogger(__name__)

EXPLORE_PROMPT = """Find the current price of this grocery item at the online shops Shwapno, Chaldal and Meena Bazar in Bangladesh.

Item: {name}
Brand: {brand}

Rules:
- Only include offers from shwapno, chaldal or meena (Meena Bazar).
- price is in whole Bangladeshi taka (BDT), as an integer.
- Only include a shop if you found the item there; do not guess prices.
- Include the product page url when you have it.
"""


class MarketService:
    def __init__(self, repo: MarketRepository, gemini: genai.Client, market_cache: RedisService):
        self.repo = repo
        self.gemini = gemini
        self.market_cache = market_cache

    async def explore(self, grocery_ids: List[UUID]) -> MarketExploreResponseSchema:
        groceries = await self.repo.get_groceries_by_ids(grocery_ids)
        found_ids = {grocery.id for grocery in groceries}

        response = MarketExploreResponseSchema(
            not_found_ids=[gid for gid in grocery_ids if gid not in found_ids],
        )

        # TODO: check cache before asking Gemini
        # one grocery at a time: the free tier has a low requests-per-minute limit
        for grocery in groceries:
            offers = await self.__ask_gemini(grocery)
            response.results.append(GroceryExploreResultSchema(
                grocery_id=grocery.id,
                offers=offers,
                cheapest=min(offers, key=lambda offer: offer.price, default=None),
            ))

        return response

    async def __ask_gemini(self, grocery: Grocery) -> List[ShopOfferSchema]:
        try:
            response = await self.gemini.aio.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=EXPLORE_PROMPT.format(name=grocery.name, brand=grocery.brand),
                config=types.GenerateContentConfig(
                    tools=[types.Tool(google_search=types.GoogleSearch())],  # without search, prices are made up
                    response_mime_type='application/json',
                    response_schema=list[ShopOfferSchema],
                ),
            )
        except Exception as e:
            logger.warning(f"Gemini explore failed for grocery {grocery.id}: {e!r}")
            raise self.__handle_gemini_error(e, grocery) from e

        if not isinstance(response.parsed, list):
            raise GeminiException(
                message=f"Gemini returned an unexpected response for '{grocery.name}'",
                detail=f"Response could not be parsed as shop offers: {(response.text or '')[:500]!r}",
            )

        return [offer for offer in response.parsed if offer.price > 0]

    @staticmethod
    def __handle_gemini_error(error: Exception, grocery: Grocery) -> GeminiException:
        """Map an error from the Gemini call to the app exception the API returns."""
        if not isinstance(error, errors.APIError):  # network errors, timeouts
            return GeminiException(
                message=f"Could not reach Gemini while exploring '{grocery.name}'",
                detail=repr(error),
            )

        detail = f"{error.code} {error.status}: {error.message}"
        if error.code == 429:
            return GeminiRateLimitException(detail=detail)
        if error.code == 503:
            return GeminiUnavailableException(detail=detail)
        return GeminiException(
            message=f"Gemini request failed while exploring '{grocery.name}'",
            detail=detail,
        )
