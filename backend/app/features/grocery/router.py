"""
Only HTTP concerns:
	•	request/response
	•	status codes
	•	dependency injection

Router should be thin.
"""
from typing import Annotated

from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db

router = APIRouter()

DbDep = Annotated[AsyncSession, Depends(get_db)]  # reusable, cleaner


@router.get("/list", status_code=status.HTTP_200_OK)
async def get_grocery_list(db: DbDep):
    return {'message': 'success list'}


@router.get("/{grocery_id}", status_code=status.HTTP_200_OK)
def get_grocery_by_id(grocery_id: str):
    return {'message': 'success get grocery by id {grocery_id}'}

#
# @router.post("/add", response_model=GroceryCreateUpdateResponseSchema, status_code=status.HTTP_201_CREATED)
# def add_grocery(request: GroceryCreateSchema):
#     return create_grocery_item(grocery_data=request, db=db)
#
#
# @router.put("/{grocery_id}", response_model=GroceryCreateUpdateResponseSchema, status_code=status.HTTP_200_OK)
# def update_grocery(grocery_id: str, request: GroceryUpdateSchema, db=Depends(get_db)):
#     return update_grocery_item(grocery_id, request, db=db)
