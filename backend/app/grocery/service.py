from fastapi import HTTPException
from datetime import datetime
from typing import Dict, Any

from .repository import GroceryRepository
from .schemas import GroceryCreate, Grocery, GroceryStockStatus, GroceryUpdate, GroceryOut


def get_stock_status(quantity: int, low_stock_threshold: int) -> GroceryStockStatus:
    """Pure business rule — easy to test separately"""
    if quantity <= low_stock_threshold:
        return GroceryStockStatus.BELOW_STOCK
    return GroceryStockStatus.IN_STOCK


def prepare_grocery_document(create_data: GroceryCreate) -> Dict[str, Any]:
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


def grocery_to_response(doc: Dict[str, Any]) -> Grocery | None:
    """
    Convert raw MongoDB document → Pydantic response model
    """
    if not doc:
        return None

    # Convert ObjectId → string
    doc["id"] = str(doc.pop("_id"))

    # Make sure datetime fields are kept as datetime (Pydantic will serialize them)
    return Grocery(**doc)


def create_grocery_item(
        grocery_data: GroceryCreate,
        db  # MongoDB database instance
) -> Grocery:
    repository = GroceryRepository(db)
    doc = prepare_grocery_document(grocery_data)
    created_doc = repository.create(doc)
    if not created_doc:
        raise HTTPException(status_code=400, detail="Failed to create grocery item")
    return grocery_to_response(created_doc)


def update_grocery_item(
        grocery_id: str,
        update_data: GroceryUpdate,
        db
) -> GroceryOut | None:
    """
    Update grocery item with partial data.
    Re-calculates stock_status when relevant fields change.
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

    # 3. Check if stock-related fields are being updated
    needs_stock_recalculation = False

    if "quantity_in_stock" in update_fields:
        needs_stock_recalculation = True

    if "low_stock_threshold" in update_fields:
        needs_stock_recalculation = True

    # 4. Re-calculate stock_status if needed
    if needs_stock_recalculation:
        # Use new values if provided, otherwise keep existing
        new_quantity = update_fields.get(
            "quantity_in_stock",
            current.get("quantity_in_stock", 0)
        )
        new_threshold = update_fields.get(
            "low_stock_threshold",
            current.get("low_stock_threshold", 10)
        )

        update_fields["stock_status"] = get_stock_status(
            new_quantity,
            new_threshold
        ).value

    # 5. Always update timestamp
    update_fields["updated_at"] = datetime.now()

    # 6. Perform the update
    updated_doc = repo.update(grocery_id, update_fields)

    if not updated_doc:
        raise HTTPException(status_code=500, detail="Failed to update grocery item")

    # 7. Return transformed response
    return grocery_to_response(updated_doc)
