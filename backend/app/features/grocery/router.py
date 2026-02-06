"""
Only HTTP concerns:
	•	request/response
	•	status codes
	•	dependency injection

Router should be thin.
"""

from fastapi import APIRouter, status, Depends

from .service import create_grocery_item, update_grocery_item, get_grocery_items, get_grocery_item
from ..db.session import get_db

from .schemas.request_schemas import GroceryCreateSchema, GroceryUpdateSchema
from .schemas.response_schemas import GroceryListDetailResponseSchema, GroceryCreateUpdateResponseSchema

router = APIRouter(
    prefix="/api/grocery",
    tags=["Grocery"],
)


@router.get("/list", response_model=list[GroceryListDetailResponseSchema], status_code=status.HTTP_200_OK)
def get_grocery_list(db=Depends(get_db)):
    return get_grocery_items(db=db)


@router.get("/{grocery_id}", response_model=GroceryListDetailResponseSchema, status_code=status.HTTP_200_OK)
def get_grocery_by_id(grocery_id: str, db=Depends(get_db)):
    return get_grocery_item(grocery_id, db=db)


@router.post("/add", response_model=GroceryCreateUpdateResponseSchema, status_code=status.HTTP_201_CREATED)
def add_grocery(request: GroceryCreateSchema, db=Depends(get_db)):
    return create_grocery_item(grocery_data=request, db=db)


@router.put("/{grocery_id}", response_model=GroceryCreateUpdateResponseSchema, status_code=status.HTTP_200_OK)
def update_grocery(grocery_id: str, request: GroceryUpdateSchema, db=Depends(get_db)):
    return update_grocery_item(grocery_id, request, db=db)
