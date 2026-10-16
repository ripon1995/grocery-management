from typing import List, Literal, Optional
from uuid import UUID

from pydantic import BaseModel

from app.common.enums import MARKET_SHOPS, ExploreJobStatus

MarketShop = Literal[tuple(shop.value for shop in MARKET_SHOPS)]


class ShopOfferSchema(BaseModel):
    """One shop's price for one grocery item. Also sent to Gemini as its response schema."""
    seller: MarketShop
    product_name: str
    price: int
    url: Optional[str] = None


class GroceryExploreResultSchema(BaseModel):
    grocery_id: UUID
    offers: List[ShopOfferSchema] = []
    cheapest: Optional[ShopOfferSchema] = None


class MarketExploreResponseSchema(BaseModel):
    results: List[GroceryExploreResultSchema] = []
    not_found_ids: List[UUID] = []


class MarketExploreJobSchema(BaseModel):
    """Returned with 202: the job runs in the worker, poll it by job_id. job_id is None when no grocery was found."""
    job_id: Optional[str] = None
    status: ExploreJobStatus
    not_found_ids: List[UUID] = []
