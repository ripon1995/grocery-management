from pydantic import BaseModel, Field, PositiveFloat, PositiveInt
from typing import Optional
from bson import ObjectId
from enum import Enum
from datetime import datetime

class GroceryType(Enum):
    WEIGHT = 'weight'
    SACK = 'sack'
    CAN = 'can'
    PIECE = 'piece'


class GroceryStockStatus(Enum):
    IN_STOCK = 'in_stock'
    BELOW_STOCK = 'below_stock'
    FULL_STOCK = 'full_stock'


class Grocery(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=100,
        description="Name of grocery item"
    )
    brand: str = Field(
        min_length=1,
        max_length=100,
        description="Brand of grocery item"
    )
    type: GroceryType = Field(
        default=GroceryType.CAN,
        description="Type of grocery item"
    )
    current_price: PositiveFloat = Field(
        ge=0,
        description="Price of grocery item"
    )
    quantity_in_stock: PositiveInt = Field(
        ge=0,
        default=0,
        description="Quantity in stock of grocery item"
    )
    best_price: PositiveFloat = Field(
        ge=0,
        description="Best price of grocery item"
    )
    best_seller: str = Field(
        min_length=1,
        max_length=100,
        description="Best seller name"
    )
    quantity_required: PositiveInt = Field(
        ge=0,
        default=0,
        description="Quantity in stock of grocery item"
    )


class GroceryCreate(Grocery):
    pass


class GroceryOut(Grocery):
    id: str = Field(..., alias="_id")                   # string version of ObjectId
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    stock_status: Optional[GroceryStockStatus] = None   # computed field

    model_config = {
        "populate_by_name": True,                       # allow alias="_id"
        "json_encoders": {ObjectId: str, datetime: lambda v: v.isoformat()},
    }
