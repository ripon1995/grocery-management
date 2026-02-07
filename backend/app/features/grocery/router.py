"""
Only HTTP concerns:
	•	request/response
	•	status codes
	•	dependency injection

Router should be thin.
"""
from typing import Annotated, List

from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db

from app.features.grocery.dependencies import get_grocery_service
from app.features.grocery.schemas.response_schemas import GroceryListResponseSchema, GroceryDetailResponseSchema
from app.features.grocery.service import GroceryService

router = APIRouter(
    prefix="/groceries",
    tags=["grocery"],
)

DbDep = Annotated[AsyncSession, Depends(get_db)]


@router.get(
    "/",
    response_model=List[GroceryListResponseSchema],
    status_code=status.HTTP_200_OK,
    summary="Get all groceries",
)
async def list_groceries(service: GroceryService = Depends(get_grocery_service)):
    items = await service.list_all_groceries()
    return items


@router.get(
    "/{grocery_id}",
    response_model=GroceryDetailResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Get grocery details",
)
async def get_grocery_by_id(grocery_id: str, service: GroceryService = Depends(get_grocery_service)):
    item = await service.get_grocery_by_id(grocery_id)
    return item
