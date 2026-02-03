from pydantic import BaseModel, Field, PositiveFloat, PositiveInt
from typing import Optional

from ..models import Grocery
from ...utils.enums import GroceryType


class GroceryCreateSchema(Grocery):
    pass


class GroceryUpdateSchema(BaseModel):
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
    quantity_in_stock: Optional[PositiveInt] = Field(
        default=None,
        ge=0,
        description="Updated required quantity"
    )
    low_stock_threshold: Optional[PositiveInt] = Field(
        default=None,
        ge=0,
        description="Updated low stock threshold"
    )
