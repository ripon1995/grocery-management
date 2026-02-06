from datetime import datetime
from typing import Optional

from ..models import GroceryBase
from ...utils.enums import GroceryStockStatus


class GroceryListDetailResponseSchema(GroceryBase):
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # All computed fields live here
    stock_status: GroceryStockStatus

    model_config = {
        "populate_by_name": True,  # allow alias="_id"
        # "json_encoders": {ObjectId: str, datetime: lambda v: v.isoformat()},
    }


class GroceryCreateUpdateResponseSchema(GroceryBase):
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
