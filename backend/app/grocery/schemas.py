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


class BestSeller(Enum):
    MEENA = 'meena'
    SHWAPNO = 'shwapno'
    LOCAL = 'local'
    COMILLA = 'comilla'


class Grocery(BaseModel):
    # required field
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
    quantity_required: PositiveInt = Field(
        ge=0,
        description="Quantity in stock of grocery item"
    )
    low_stock_threshold: PositiveInt = Field(
        ge=0,
        default=1,
        description="Minimum quantity in stock of grocery item"
    )


class GroceryCreate(Grocery):
    pass


class GroceryUpdate(BaseModel):
    """Used for PATCH /groceries/{id}"""
    name: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=100,
        description="New name of grocery item"
    )
    brand: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=100,
        description="New brand name"
    )
    type: Optional[GroceryType] = Field(
        default=None,
        description="New type of grocery item"
    )
    current_price: Optional[PositiveFloat] = Field(
        default=None,
        ge=0,
        description="Updated current price"
    )
    quantity_required: Optional[PositiveInt] = Field(
        default=None,
        ge=0,
        description="Updated required quantity"
    )
    low_stock_threshold: Optional[PositiveInt] = Field(
        default=None,
        ge=0,
        description="Updated low stock threshold"
    )


class GroceryOut(Grocery):
    id: str = Field(..., alias="_id")  # string version of ObjectId
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
