import logging
import uuid
import json
from typing import List
from uuid import UUID

import aio_pika
from aio_pika.abc import AbstractRobustChannel
from app.utils.redis_key_helper import RedisKeyHelper
from app.common.enums import ExploreJobStatus
from app.core.config import settings
from app.services.redis_service import RedisService
from .queues.explore_queue import EXPLORE_JOBS_QUEUE

logger = logging.getLogger(__name__)


class MarketJobQueueService:
    def __init__(
            self,
            rabbitmq_channel: AbstractRobustChannel,
            redis_service: RedisService
    ):
        self.rabbitmq_channel = rabbitmq_channel
        self.redis_service = redis_service

    # -----------------------------------------------------------------------------------------------
    # private methods with single responsibilities
    # -----------------------------------------------------------------------------------------------
    @staticmethod
    def __job_key(job_id: str) -> str:
        return f"{RedisKeyHelper.EXPLORE_JOB_KEY_PREFIX.value}:{job_id}"

    # -----------------------------------------------------------------------------------------------
    # exposed methods
    # -----------------------------------------------------------------------------------------------

    async def get_job(self, job_id: str) -> dict | None:
        return await self.redis_service.get(self.__job_key(job_id))

    async def save_job(self, job: dict) -> None:
        await self.redis_service.set(self.__job_key(job['job_id']), job, ttl=settings.EXPLORE_JOB_TTL_S)

    async def enqueue_job(self, grocery_ids: List[UUID]) -> str:
        """Record the job as pending in Redis, then publish it to the explore queue. Returns the job id."""
        job_id = str(uuid.uuid4())
        ids = [str(grocery_id) for grocery_id in grocery_ids]

        # 1. Save the job state first, so the worker always finds it
        await self.save_job({
            "job_id": job_id,
            "status": ExploreJobStatus.PENDING.value,
            "grocery_ids": ids,
            "results": [],
        })
        # 2. Publish the task message to RabbitMQ
        message = aio_pika.Message(
            body=json.dumps({
                "job_id": job_id,
                "grocery_ids": ids,
                "retry_count": 0,
            }).encode("utf-8"),
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            content_type="application/json",
            correlation_id=job_id,
        )
        try:
            # mandatory: the broker rejects a message no queue receives instead of dropping it
            await self.rabbitmq_channel.default_exchange.publish(
                message, routing_key=EXPLORE_JOBS_QUEUE, mandatory=True,
            )
        except Exception:
            await self.redis_service.delete(self.__job_key(job_id))  # never leave a job that no worker will pick up
            raise

        logger.info(f"Enqueued explore job {job_id} for {len(ids)} items")
        return job_id
