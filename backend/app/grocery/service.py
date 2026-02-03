from fastapi import HTTPException
from datetime import datetime
from typing import Dict, Any

from pydantic.v1 import PositiveFloat

from .repository import GroceryRepository
from .schemas.response_schemas import GroceryListDetailResponseSchema, GroceryCreateUpdateResponseSchema
from .schemas.request_schemas import GroceryCreateSchema, GroceryUpdateSchema
from ..utils.enums import GroceryStockStatus


def __get_stock_status(quantity: int, low_stock_threshold: int) -> GroceryStockStatus:
    """Pure business rule — easy to test separately"""
    if quantity <= low_stock_threshold:
        return GroceryStockStatus.BELOW_STOCK
    return GroceryStockStatus.IN_STOCK

# TODO -> check this
def __calculate_best_price(new_price: float, best_price: float) -> float:
    return min(new_price, best_price)


def prepare_grocery_document(create_data: GroceryCreateSchema) -> Dict[str, Any]:
    """
    Prepare MongoDB document with timestamps and any computed fields
    """
    now = datetime.now()
    return {
        **create_data.model_dump(mode='json'),
        "created_at": now,
        "updated_at": now,
        # You can add more automatic fields here if needed
        # e.g. "stock_status": compute_stock_status(create_data.quantity_in_stock),
    }


def grocery_to_response(doc: Dict[str, Any]) -> GroceryCreateUpdateResponseSchema | None:
    """
    Convert raw MongoDB document → Pydantic response model
    """
    if not doc:
        return None

    # Convert ObjectId → string
    doc["id"] = str(doc.pop("_id"))

    # Make sure datetime fields are kept as datetime (Pydantic will serialize them)
    return GroceryCreateUpdateResponseSchema(**doc)


def grocery_to_list_detail_response(doc: Dict[str, Any]) -> GroceryListDetailResponseSchema | None:
    """
    Convert raw MongoDB document → Pydantic response model
    """
    if not doc:
        return None

    # Convert ObjectId → string
    doc["id"] = str(doc.pop("_id"))
    doc['best_price'] = 10000.89
    doc['best_seller'] = 'meena'
    doc['stock_status'] = __get_stock_status(doc['quantity_in_stock'], doc['low_stock_threshold'])

    # Make sure datetime fields are kept as datetime (Pydantic will serialize them)
    return GroceryListDetailResponseSchema(**doc)


def create_grocery_item(
        grocery_data: GroceryCreateSchema,
        db
) -> GroceryCreateUpdateResponseSchema:
    repository = GroceryRepository(db)
    doc = prepare_grocery_document(grocery_data)
    created_doc = repository.create(doc)
    if not created_doc:
        raise HTTPException(status_code=400, detail="Failed to create grocery item")
    return grocery_to_response(created_doc)


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
    # TODO -> Check this
    update_fields['best_price'] = __calculate_best_price(update_fields['current_price'], current['best_price'])

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
