from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, ConfigDict, computed_field

from app.common.enums import GroceryType, Seller, GroceryStockStatus


class GroceryBaseResponseSchema(BaseModel):
    id: UUID
    name: str
    brand: str
    type: GroceryType
    current_price: float
    current_seller: Seller
    low_stock_threshold: int
    quantity_in_stock: int
    should_include: bool
    best_seller: Seller
    best_price: float

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            GroceryType: lambda v: v.value,
            Seller: lambda v: v.value,
            UUID: lambda v: str(v)
        }
    )

    @computed_field(return_type=GroceryStockStatus)
    @property
    def stock_status(self) -> GroceryStockStatus:
        """Computed stock status based on quantity and threshold"""
        if self.quantity_in_stock <= self.low_stock_threshold:
            return GroceryStockStatus.BELOW_STOCK
        return GroceryStockStatus.IN_STOCK


class GroceryListResponseSchema(GroceryBaseResponseSchema):
    pass


class GroceryDetailResponseSchema(GroceryBaseResponseSchema):
    created_at: datetime
    updated_at: datetime


class GroceryCreateResponseSchema(GroceryBaseResponseSchema):
    created_at: datetime


class GroceryUpdateResponseSchema(GroceryBaseResponseSchema):
    updated_at: datetime
