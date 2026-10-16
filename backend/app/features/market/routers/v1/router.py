from typing import Annotated

from fastapi import APIRouter, Body, Depends
from starlette import status

from app.core.api_response_schema import ApiResponseSchema
from app.features.market.dependencies import get_market_service
from app.features.market.schemas.request_schemas import MarketExploreRequestSchema
from app.features.market.schemas.response_schemas import MarketExploreJobSchema
from app.features.market.service import MarketService

router = APIRouter(
    prefix="/v1/market",
    tags=["market"]
)


@router.post(
    path='/explore',
    status_code=status.HTTP_202_ACCEPTED,  # the worker does the Gemini calls; poll the job for results
    summary='Queue a market explore job',
    response_model=ApiResponseSchema[MarketExploreJobSchema],
)
async def explore(
        data: Annotated[MarketExploreRequestSchema, Body()],
        market_service: MarketService = Depends(get_market_service),
):
    result = await market_service.explore(data.grocery_ids)
    return ApiResponseSchema(
        success=True,
        data=result,
        message="Market explore job queued",
    )
