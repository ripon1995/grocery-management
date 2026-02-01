from fastapi import HTTPException
from datetime import datetime
from typing import Dict, Any

from .repository import GroceryRepository
from .schemas import GroceryCreate, Grocery


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
