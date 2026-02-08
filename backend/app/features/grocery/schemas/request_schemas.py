from typing import Optional

from pydantic import BaseModel, Field, PositiveInt

from app.common.enums import GroceryType, Seller


class GroceryCreateSchema(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=100,
        description="New grocery name"
    )
    brand: str = Field(
        min_length=1,
        max_length=100,
        description="New brand name"
    )
    type: GroceryType = Field(
        description="Type of grocery item"
    )
    current_price: PositiveInt = Field(
        ge=0,
        le=100000,
        description="Current price of the grocery item"
    )
    current_seller: Seller = Field(
        description="Current seller of grocery item"
    )
    low_stock_threshold: PositiveInt = Field(
        ge=0,
        description="Low stock threshold for grocery item"
    )
    quantity_in_stock: PositiveInt = Field(
        ge=0,
        description="Stock quantity in grocery item"
    )


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
    current_price: Optional[PositiveInt] = Field(
        default=None,
        ge=0,
        le=100000,
        description="Updated current price"
    )
    current_seller: Optional[Seller] = Field(
        description="Seller of grocery item"
    )
    low_stock_threshold: Optional[PositiveInt] = Field(
        default=None,
        ge=0,
        description="Updated low stock threshold"
    )
    quantity_in_stock: Optional[PositiveInt] = Field(
        default=None,
        ge=0,
        description="Updated required quantity"
    )
    should_include: Optional[bool] = Field(
        description="Should include grocery item for this time"
    )
