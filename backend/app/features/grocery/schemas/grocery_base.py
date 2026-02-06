"""
Pydantic schemas only
NO DB LOGIC
"""


from pydantic import BaseModel, Field, PositiveFloat, PositiveInt
from backend.app.utils.enums import GroceryType, Seller


from sqlalchemy import String

# base model talks with user only
class GroceryBase(BaseModel):
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
        default=GroceryType.CAN.value,
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
    current_seller: str = Field(
        default=Seller.MEENA.value,
        description="Seller of grocery item"
    )
