from pydantic import BaseModel, ConfigDict

from app.common.enums import GroceryType, Seller


class GroceryListDetailResponseSchema(BaseModel):
    name: str
    brand: str
    type: GroceryType
    current_price: float
    current_seller: Seller
    low_stock_threshold: int
    quantity_in_stock: int
    should_include: bool

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            GroceryType: lambda v: v.value,
            Seller: lambda v: v.value,
        }
    )
