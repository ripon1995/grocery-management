from fastapi import APIRouter, status, Depends

from .service import create_grocery_item
from ..database.database_client import get_db

from .schemas import Grocery, GroceryCreate

router = APIRouter(
    prefix="/api/grocery",
    tags=["Grocery"],
)


@router.get("/list")
def get_grocery_list():
    return {"message": "Should return grocery list"}


@router.get("/item/{id}")
def get_grocery_by_id():
    return {"message": f"Should return a single item {id}"}


@router.post("/add", response_model=Grocery, status_code=status.HTTP_201_CREATED)
def add_grocery(request: GroceryCreate, db=Depends(get_db)):
    return create_grocery_item(grocery_data=request, db=db)
