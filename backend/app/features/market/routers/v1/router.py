from typing import Annotated

from fastapi import APIRouter, Body, Depends
from starlette import status

from app.core.api_response_schema import ApiResponseSchema
from app.features.market.dependencies import get_market_service
from app.features.market.schemas.request_schemas import MarketExploreRequestSchema
from app.features.market.schemas.response_schemas import MarketExploreResponseSchema
from app.features.market.service import MarketService

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
async def explore(
        data: Annotated[MarketExploreRequestSchema, Body()],
        market_service: MarketService = Depends(get_market_service),
):
    result = await market_service.explore(data.grocery_ids)
    return ApiResponseSchema(
        success=True,
        data=result,
        message="Market explore successful",
    )
