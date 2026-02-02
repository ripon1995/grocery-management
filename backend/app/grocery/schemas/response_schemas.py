from pydantic import PositiveFloat, PositiveInt
from typing import Optional
from bson import ObjectId
from datetime import datetime
from ..models import Grocery
from ...utils.enums import BestSeller, GroceryStockStatus


class GroceryListDetailResponseSchema(Grocery):
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # All computed fields live here
    quantity_in_stock: PositiveInt
    best_price: PositiveFloat
    best_seller: BestSeller
    stock_status: GroceryStockStatus

    model_config = {
        "populate_by_name": True,  # allow alias="_id"
        "json_encoders": {ObjectId: str, datetime: lambda v: v.isoformat()},
    }


class GroceryCreateUpdateResponseSchema(Grocery):
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None