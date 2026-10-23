import logging
from typing import List
from google import genai
from google.genai import errors, types
from starlette import status

from app.clients.fake_gemini_client import FakeGeminiClient
from app.core.config import settings
from app.core.exceptions import (
    GeminiException,
    GeminiRateLimitException,
    GeminiUnavailableException,
)

from app.features.grocery.models import Grocery
from schemas.response_schemas import ShopOfferSchema

logger = logging.getLogger(__name__)


class MarketExplorer:
    def __init__(self, gemini: genai.Client | FakeGeminiClient):
        logger.debug("Initializing MarketExplorerWorkerService")
        self.gemini = gemini
        self.EXPLORE_PROMPT = """Find the current price of this grocery item at the online shops Shwapno, Chaldal and Meena Bazar in Bangladesh.

        Item: {name}
        Brand: {brand}

        Rules:
        - Only include offers from shwapno, chaldal or meena (Meena Bazar).
        - price is in whole Bangladeshi taka (BDT), as an integer.
        - Only include a shop if you found the item there; do not guess prices.
        - Include the product page url when you have it.
        """

    # -----------------------------------
    # private methods
    # -----------------------------------

    async def __ask_gemini(self, grocery: Grocery) -> List[ShopOfferSchema]:
        try:
            response = await self.gemini.aio.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=self.EXPLORE_PROMPT.format(name=grocery.name, brand=grocery.brand),
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
        if error.code == status.HTTP_429_TOO_MANY_REQUESTS:
            return GeminiRateLimitException(detail=detail)
        if error.code == status.HTTP_503_SERVICE_UNAVAILABLE:
            return GeminiUnavailableException(detail=detail)
        return GeminiException(
            message=f"Gemini request failed while exploring '{grocery.name}'",
            detail=detail,
        )

    # -----------------------------------
    # exposed methods
    # -----------------------------------