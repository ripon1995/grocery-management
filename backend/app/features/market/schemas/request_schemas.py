from typing import List
from uuid import UUID

from pydantic import BaseModel, Field


class MarketExploreRequestSchema(BaseModel):
    grocery_ids: List[UUID] = Field(
        min_length=1,
        description="Ids of the grocery items to update"
    )
