"""
service.py — Business logic layer

Where real logic lives.

Examples:
	•	validation rules
	•	permissions
	•	workflows
	•	orchestration across repositories

Service calls' repository.

Router calls service.

Never skip this layer in large apps.
"""

from typing import Tuple, List

from app.common.enums import Seller, GroceryStockStatus
from .models import Grocery
from .repository import GroceryRepository
from .schemas.request_schemas import GroceryCreateSchema, GroceryUpdateSchema
from .schemas.response_schemas import (
    GroceryListResponseSchema,
    GroceryDetailResponseSchema,
    GroceryCreateResponseSchema, GroceryUpdateResponseSchema
)


class GroceryService:
    def __init__(self, repo: GroceryRepository):
        self.repo = repo

    # ───────────────────────────────────────────────
    # Business rule helpers
    # ───────────────────────────────────────────────
    @staticmethod
    def __update_best_price_and_best_seller(
            new_price: float,
            best_price: float,
            new_seller: Seller,
            best_seller: Seller,
    ) -> Tuple[float, Seller]:
        if best_price is None:
            best_price = new_price
            best_seller = Seller.MEENA
            return best_price, best_seller
        if new_price < best_price:
            best_price = new_price
            best_seller = new_seller

        return best_price, best_seller

    @staticmethod
    def __get_stock_status(
            quantity: int,
            low_stock_threshold: int,
    ) -> GroceryStockStatus:
        if quantity <= low_stock_threshold:
            return GroceryStockStatus.BELOW_STOCK
        return GroceryStockStatus.IN_STOCK

    # ───────────────────────────────────────────────
    # Prepare / mapping methods
    # ───────────────────────────────────────────────
    @staticmethod
    def __prepare_grocery(data: GroceryCreateSchema) -> Grocery:
        """Map create schema → ORM model + apply business defaults/rules"""
        values = data.model_dump()
        values["current_price"] = float(data.current_price)
        values["best_seller"] = values["current_seller"]
        values["best_price"] = values["current_price"]
        return Grocery(**values)

    def __prepare_grocery_for_update(self, grocery: Grocery, data: GroceryUpdateSchema) -> Grocery:
        update_values = data.model_dump(exclude_unset=True)
        for key, value in update_values.items():
            if hasattr(grocery, key):
                setattr(grocery, key, value)

        if "current_price" in update_values or "current_seller" in update_values:
            best_price, best_seller = self.__update_best_price_and_best_seller(
                update_values.get("current_price", grocery.current_price),
                grocery.best_price,
                update_values.get("current_seller", grocery.current_seller),
                grocery.best_seller
            )
            grocery.best_price = best_price
            grocery.best_seller = best_seller

        return grocery

    # ───────────────────────────────────────────────
    # Public API methods
    # ───────────────────────────────────────────────

    async def list_all_groceries(self) -> List[GroceryListResponseSchema]:
        groceries = await self.repo.get_groceries()
        return [GroceryListResponseSchema.model_validate(item) for item in groceries]

    async def get_grocery_by_id(self, grocery_id) -> GroceryDetailResponseSchema:
        grocery = await self.repo.get_by_id(grocery_id)
        return GroceryDetailResponseSchema.model_validate(grocery)

    async def create_grocery(self, data: GroceryCreateSchema) -> GroceryCreateResponseSchema:
        grocery = self.__prepare_grocery(data)
        created_grocery = await self.repo.add_grocery(grocery)
        return GroceryCreateResponseSchema.model_validate(created_grocery)

    async def update_grocery(self, grocery_id: str, data: GroceryUpdateSchema) -> GroceryUpdateResponseSchema:
        grocery = await self.repo.get_by_id(grocery_id)
        updated_grocery_data = self.__prepare_grocery_for_update(grocery, data)
        updated_grocery = await self.repo.update_grocery(updated_grocery_data)
        return GroceryUpdateResponseSchema.model_validate(updated_grocery)
