from datetime import datetime
from typing import Dict, Any, Tuple

from fastapi import HTTPException

from .models import Grocery
from .repository import GroceryRepository
from .schemas.request_schemas import GroceryCreateSchema, GroceryUpdateSchema
from .schemas.response_schemas import GroceryListDetailResponseSchema, GroceryCreateUpdateResponseSchema
from ..utils.enums import GroceryStockStatus, Seller


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


def prepare_grocery_model(create_data: GroceryCreateSchema) -> Grocery:
    grocery = Grocery(
        **create_data.model_dump(mode='json'),
        best_price=create_data.current_price,
        best_seller=create_data.current_seller
    )

    return grocery


def grocery_to_response(grocery: Grocery) -> GroceryCreateUpdateResponseSchema | None:
    """
    Convert raw MongoDB document → Pydantic response model
    """
    if not grocery:
        return None

    # Make sure datetime fields are kept as datetime (Pydantic will serialize them)
    return GroceryCreateUpdateResponseSchema(**grocery.model_dump(mode="json"))


def create_grocery_item(
        grocery_data: GroceryCreateSchema,
        db
) -> GroceryCreateUpdateResponseSchema:
    repository = GroceryRepository(db)
    internal_model = prepare_grocery_model(grocery_data)
    created_grocery = repository.create(internal_model)
    if not created_grocery:
        raise HTTPException(status_code=400, detail="Failed to create grocery item")
    return grocery_to_response(created_grocery)


################ updated ###################
def grocery_to_list_detail_response(doc: Dict[str, Any]) -> GroceryListDetailResponseSchema | None:
    """
    Convert raw MongoDB document → Pydantic response model
    """
    if not doc:
        return None

    # Convert ObjectId → string
    doc["id"] = str(doc.pop("_id"))
    # display information
    # not stored in backend
    # only calculated on the fly
    doc['stock_status'] = __get_stock_status(doc['quantity_in_stock'], doc['low_stock_threshold'])

    # Make sure datetime fields are kept as datetime (Pydantic will serialize them)
    return GroceryListDetailResponseSchema(**doc)


def update_grocery_item(
        grocery_id: str,
        update_data: GroceryUpdateSchema,
        db
) -> GroceryCreateUpdateResponseSchema | None:
    """
    Update grocery item with partial data.
    """
    repo = GroceryRepository(db)

    # 1. Fetch current document
    current = repo.find_by_id(grocery_id)
    if not current:
        raise HTTPException(status_code=404, detail="Grocery item not found")

    # 2. Prepare update payload
    update_fields = update_data.model_dump(mode="json", exclude_unset=True)

    # If nothing was sent → return current state (no-op update)
    if not update_fields:
        return grocery_to_response(current)

    # 5. Always update timestamp
    update_fields["updated_at"] = datetime.now()
    update_fields['best_price'], update_fields['best_seller'] = __update_best_price_and_best_seller(
        update_fields['current_price'], current['best_price'],
        update_fields['current_seller'], current['best_seller']
    )

    # 6. Perform the update
    updated_doc = repo.update(grocery_id, update_fields)

    if not updated_doc:
        raise HTTPException(status_code=500, detail="Failed to update grocery item")

    # 7. Return transformed response
    return grocery_to_response(updated_doc)


def get_grocery_item(grocery_id: str, db) -> GroceryListDetailResponseSchema | None:
    repository = GroceryRepository(db)
    doc = repository.find_by_id(grocery_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Grocery item not found")

    return grocery_to_list_detail_response(doc)


def get_grocery_items(db) -> list[GroceryListDetailResponseSchema]:
    repository = GroceryRepository(db)
    docs = repository.find_all()
    return list(map(lambda doc: grocery_to_list_detail_response(doc), docs))
