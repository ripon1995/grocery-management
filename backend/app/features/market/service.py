"""
service.py — Business logic layer
"""

import logging
from typing import List
from uuid import UUID

from app.common.enums import ExploreJobStatus, MailJobStatus
from app.core.exceptions import ResourceNotFoundException
from .email_service import EmailService
from .repository import MarketRepository
from .job_queue_service import MarketJobQueueService, JobType
from .schemas.response_schemas import (
    MarketExploreJobSchema,
    MarketExploreJobStatusSchema,
    EmailJobResponseSchema
)

logger = logging.getLogger(__name__)


class MarketService:
    def __init__(
            self,
            repo: MarketRepository,
            job: MarketJobQueueService,
            email: EmailService
    ):
        self.repo = repo
        self.job = job
        self.email = email

    async def explore(self, grocery_ids: List[UUID]) -> MarketExploreJobSchema:
        """Queue the found groceries for the worker; missing IDs are reported straight away."""
        groceries = await self.repo.get_groceries_by_ids(grocery_ids)
        found_ids = {grocery.id for grocery in groceries}
        not_found_ids = [gid for gid in grocery_ids if gid not in found_ids]

        if not found_ids:  # nothing to explore, so no job
            return MarketExploreJobSchema(status=ExploreJobStatus.DONE, not_found_ids=not_found_ids)

        job_id = await self.job.enqueue_job([gid for gid in grocery_ids if gid in found_ids])
        return MarketExploreJobSchema(job_id=job_id, status=ExploreJobStatus.PENDING, not_found_ids=not_found_ids)

    async def get_explore_job(self, job_id: UUID) -> MarketExploreJobStatusSchema:
        """Read the job's progress from Redis, so any API instance can answer the poll."""
        job = await self.job.get_job(str(job_id), JobType.EXPLORE)
        if job is None:
            raise ResourceNotFoundException(
                message="Explore job not found or expired",
                detail=f"No explore job {job_id}; jobs are kept for a limited time after they're queued",
            )
        # extra keys such as grocery_ids are ignored by the schema
        return MarketExploreJobStatusSchema(**job, total=len(job['grocery_ids']))

    async def send_email(self) -> EmailJobResponseSchema:
        # offload to email service
        result = await self.email.send_email()
        job_id = await self.job.enqueue_email(result)
        # get result
        return EmailJobResponseSchema(job_id=job_id, status=MailJobStatus.PENDING)
