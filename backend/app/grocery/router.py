from fastapi import APIRouter, status, Depends

from .service import create_grocery_item, update_grocery_item
from ..database.database_client import get_db

from .schemas import Grocery, GroceryCreate, GroceryUpdate

router = APIRouter(
    prefix="/api/grocery",
    tags=["Grocery"],
)


@router.get("/list")
def get_grocery_list():
    return {"message": "Should return grocery list"}


@router.get("/{id}")
def get_grocery_by_id():
    return {"message": f"Should return a single item {id}"}


@router.post("/add", response_model=Grocery, status_code=status.HTTP_201_CREATED)
def add_grocery(request: GroceryCreate, db=Depends(get_db)):
    return create_grocery_item(grocery_data=request, db=db)


@router.put("/{grocery_id}", response_model=Grocery, status_code=status.HTTP_200_OK)
def update_grocery(grocery_id: str, request: GroceryUpdate, db=Depends(get_db)):
    return update_grocery_item(grocery_id, request, db=db)
