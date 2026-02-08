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
from app.features.grocery.schemas.request_schemas import GroceryCreateSchema, GroceryUpdateSchema
from app.features.grocery.schemas.response_schemas import GroceryListResponseSchema, GroceryDetailResponseSchema, \
    GroceryCreateResponseSchema, GroceryUpdateResponseSchema
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
async def list_groceries(grocery_service: GroceryService = Depends(get_grocery_service)):
    items = await grocery_service.list_all_groceries()
    return items


@router.get(
    "/{grocery_id}",
    response_model=GroceryDetailResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Get grocery details",
)
async def get_grocery_by_id(
        grocery_id: str,
        grocery_service: GroceryService = Depends(get_grocery_service)
):
    item = await grocery_service.get_grocery_by_id(grocery_id)
    return item


@router.post(
    "/",
    response_model=GroceryCreateResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new grocery item",
)
async def create_grocery(
        data: GroceryCreateSchema = GroceryCreateSchema,
        grocery_service: GroceryService = Depends(get_grocery_service)
):
    return await grocery_service.create_grocery(data)


@router.put(
    "/{grocery_id}",
    response_model=GroceryUpdateResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Update a grocery item",
)
async def update_grocery(
        grocery_id: str,
        data: GroceryUpdateSchema = GroceryUpdateSchema,
        grocery_service: GroceryService = Depends(get_grocery_service)
):
    return await grocery_service.update_grocery(grocery_id, data)
