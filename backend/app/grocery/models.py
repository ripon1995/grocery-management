from pydantic import BaseModel, Field, PositiveFloat, PositiveInt, Optional

from backend.app.utils.enums import GroceryType


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
        description="Quantity in stock of grocery item"
    )
    low_stock_threshold: PositiveInt = Field(
        ge=0,
        default=1,
        description="Minimum quantity in stock of grocery item"
    )
    # TODO -> check this
    # calculated field
    best_price: Optional[PositiveFloat] = Field(
        default=None,
        description="Lowest price recorded. Defaults to current_price if not provided."
    )
