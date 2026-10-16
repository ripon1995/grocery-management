from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, HttpUrl

from app.common.enums import Seller, PriceSource


class ShopOfferSchema(BaseModel):
    """One shop's price for one grocery item, as found by Gemini"""
    seller: Seller
    product_name: str
    price: int
    pack_size: Optional[str] = None
    url: Optional[HttpUrl] = None
    in_stock: Optional[bool] = None


class GroceryExploreResultSchema(BaseModel):
    grocery_id: UUID
    name: str
    brand: str
    current_price: int
    current_seller: Seller
    offers: List[ShopOfferSchema] = []
    cheapest: Optional[ShopOfferSchema] = None
    savings: Optional[int] = None
    source: PriceSource = PriceSource.GEMINI
    explored_at: datetime
    from_cache: bool = False

    model_config = ConfigDict(from_attributes=True)


class MarketExploreResponseSchema(BaseModel):
    results: List[GroceryExploreResultSchema] = []
    not_found_ids: List[UUID] = []
    failed_ids: List[UUID] = []
