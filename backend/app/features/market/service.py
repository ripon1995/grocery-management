"""
service.py — Business logic layer
"""

import logging
from typing import List
from uuid import UUID
from app.common.enums import ExploreJobStatus
from .repository import MarketRepository
from .job_queue_service import MarketJobQueueService
from .schemas.response_schemas import MarketExploreJobSchema

logger = logging.getLogger(__name__)


class MarketService:
    def __init__(
            self,
            repo: MarketRepository,
            job: MarketJobQueueService
    ):
        self.repo = repo
        self.job = job

    async def explore(self, grocery_ids: List[UUID]) -> MarketExploreJobSchema:
        """Queue the found groceries for the worker; missing IDs are reported straight away."""
        groceries = await self.repo.get_groceries_by_ids(grocery_ids)
        found_ids = {grocery.id for grocery in groceries}
        not_found_ids = [gid for gid in grocery_ids if gid not in found_ids]

        if not found_ids:  # nothing to explore, so no job
            return MarketExploreJobSchema(status=ExploreJobStatus.DONE, not_found_ids=not_found_ids)

        job_id = await self.job.enqueue_job([gid for gid in grocery_ids if gid in found_ids])
        return MarketExploreJobSchema(job_id=job_id, status=ExploreJobStatus.PENDING, not_found_ids=not_found_ids)
