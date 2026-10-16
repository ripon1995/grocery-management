from typing import Annotated

from fastapi import APIRouter, Body
from starlette import status

from app.core.api_response_schema import ApiResponseSchema
from app.features.market.schemas.request_schemas import MarketExploreRequestSchema
from app.features.market.schemas.response_schemas import MarketExploreResponseSchema

router = APIRouter(
    prefix="/v1/market",
    tags=["market"]
)


@router.post(
    path='/explore',
    status_code=status.HTTP_200_OK,
    summary='Explore market data',
    response_model=ApiResponseSchema[MarketExploreResponseSchema],
)
async def explore(data: Annotated[MarketExploreRequestSchema, Body()]):
    return ApiResponseSchema(
        success=True,
        data=MarketExploreResponseSchema(),
        message="Market explore successful",
    )
