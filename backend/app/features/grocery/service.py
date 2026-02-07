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
from .repository import GroceryRepository
from .schemas.response_schemas import GroceryListDetailResponseSchema


class GroceryService:
    def __init__(self, repo: GroceryRepository):
        self.repo = repo

    async def list_all_groceries(self) -> List[GroceryListDetailResponseSchema]:
        groceries = await self.repo.get_groceries()

        return [GroceryListDetailResponseSchema.model_validate(item) for item in groceries]


########################################################################################################################################
# TODO -> Refactor the following


def __get_stock_status(quantity: int, low_stock_threshold: int) -> GroceryStockStatus:
    """Pure business rule — easy to test separately"""
    if quantity <= low_stock_threshold:
        return GroceryStockStatus.BELOW_STOCK
    return GroceryStockStatus.IN_STOCK


def __update_best_price_and_best_seller(
        new_price: float,
        best_price: float,
        new_seller: str,
        best_seller: str,
) -> Tuple[float, str]:
    if best_price is None:
        best_price = new_price
        best_seller = Seller.MEENA.value
        return best_price, best_seller
    if new_price < best_price:
        best_price = new_price
        best_seller = new_seller

    return best_price, best_seller

# def prepare_grocery_model(create_data: GroceryCreateSchema) -> Grocery:
#     grocery = Grocery(
#         **create_data.model_dump(mode='json'),
#         best_price=create_data.current_price,
#         best_seller=create_data.current_seller
#     )
#
#     return grocery


# def grocery_to_response(grocery: Grocery) -> GroceryCreateUpdateResponseSchema | None:
#     """
#     Convert raw MongoDB document → Pydantic response model
#     """
#     if not grocery:
#         return None
#
#     # Make sure datetime fields are kept as datetime (Pydantic will serialize them)
#     return GroceryCreateUpdateResponseSchema(**grocery.model_dump(mode="json"))


# def create_grocery_item(
#         grocery_data: GroceryCreateSchema,
#         db
# ) -> GroceryCreateUpdateResponseSchema:
#     repository = GroceryRepository(db)
#     internal_model = prepare_grocery_model(grocery_data)
#     created_grocery = repository.create(internal_model)
#     if not created_grocery:
#         raise HTTPException(status_code=400, detail="Failed to create grocery item")
#     return grocery_to_response(created_grocery)
#

# def update_grocery_item(
#         grocery_id: str,
#         update_data: GroceryUpdateSchema,
#         db
# ) -> GroceryCreateUpdateResponseSchema | None:
#     """
#     Update grocery item with partial data.
#     """
#     repo = GroceryRepository(db)
#
#     # 1. Fetch current document
#     current_grocery = repo.find_by_id(grocery_id)
#     if not current_grocery:
#         raise HTTPException(status_code=404, detail="Grocery item not found")
#
#     # 2. Prepare update payload
#     update_fields = update_data.model_dump(mode="json", exclude_unset=True)
#
#     # If nothing was sent → return current state (no-op update)
#     if not update_fields:
#         return grocery_to_response(current_grocery)
#
#     # 5. Always update timestamp
#     new_price = update_fields.get("current_price", current_grocery.current_price)
#     new_seller = update_fields.get("current_seller", current_grocery.current_seller)
#
#     # Calculate the new best pair
#     best_p, best_s = __update_best_price_and_best_seller(
#         new_price,
#         current_grocery.best_price,
#         new_seller,
#         current_grocery.best_seller
#     )
#     update_fields["best_price"] = best_p
#     update_fields["best_seller"] = best_s
#
#     # 6. Perform the update
#     updated_grocery = repo.update(grocery_id, update_fields)
#
#     if not updated_grocery:
#         raise HTTPException(status_code=500, detail="Failed to update grocery item")
#
#     # 7. Return transformed response
#     return grocery_to_response(updated_grocery)


# def grocery_to_list_detail_response(grocery: Grocery) -> GroceryListDetailResponseSchema | None:
#     if not grocery:
#         return None
#     stock_status = __get_stock_status(grocery.quantity_in_stock, grocery.low_stock_threshold)
#     response_data = grocery.model_dump()
#     response_data["stock_status"] = stock_status
#     return GroceryListDetailResponseSchema(**response_data)

# def get_grocery_item(grocery_id: str, db) -> GroceryListDetailResponseSchema | None:
#     repository = GroceryRepository(db)
#     grocery = repository.find_by_id(grocery_id)
#     if not grocery:
#         raise HTTPException(status_code=404, detail="Grocery item not found")
#
#     return grocery_to_list_detail_response(grocery)
