from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Body, Depends
from starlette import status

from app.core.api_response_schema import ApiResponseSchema
from app.features.market.dependencies import get_market_service
from app.features.market.schemas.request_schemas import MarketExploreRequestSchema
from app.features.market.schemas.response_schemas import MarketExploreJobSchema, MarketExploreJobStatusSchema
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


@router.get(
    path='/explore/jobs/{job_id}',
    summary='Get an explore job and the results so far',
    response_model=ApiResponseSchema[MarketExploreJobStatusSchema],
)
async def get_explore_job(
        job_id: UUID,  # a malformed id is a 422 before it reaches Redis
        market_service: MarketService = Depends(get_market_service),
):
    result = await market_service.get_explore_job(job_id)
    return ApiResponseSchema(
        success=True,
        data=result,
        message="Market explore job fetched",
    )
