import logging
import json
from uuid import UUID

from aio_pika.abc import AbstractRobustChannel, AbstractIncomingMessage

from app.common.enums import ExploreJobStatus
from app.db.session import async_session_factory
from app.features.market.job_queue_service import MarketJobQueueService
from app.features.market.market_explorer import MarketExplorer
from app.features.market.queues.explore_queue import EXPLORE_JOBS_QUEUE
from app.features.market.repository import MarketRepository

logger = logging.getLogger(__name__)

class ExploreJobConsumer:

    def __init__(
            self,
            channel: AbstractRobustChannel,
            explorer: MarketExplorer,
            job_service: MarketJobQueueService
    ) -> None:
        self.channel = channel
        self.explorer = explorer
        self.job_service = job_service


    async def start(self) -> None:
        job_queue = await self.channel.get_queue(EXPLORE_JOBS_QUEUE)
        await job_queue.consume(self.__on_message)


    async def __on_message(self, message: AbstractIncomingMessage) -> None:
        async with message.process(requeue=False):
            body = json.loads(message.body)
            logger.info(f"⚙️ [WORKER] job {body['job_id']} received (redelivered={message.redelivered})")
            await self.__run_job(body['job_id'])



    async def __run_job(self, job_id: str) -> None:
        job = await self.job_service.get_job(job_id)
        if job is None:
            return
        job['status'] = ExploreJobStatus.RUNNING.value
        await self.job_service.save_job(job)

        async with async_session_factory() as session:
            groceries = await MarketRepository(session).get_groceries_by_ids([UUID(gid) for gid in job['grocery_ids']])
            for grocery in groceries:
                result = await self.explorer.explore_grocery(grocery)
                job['results'].append(result.model_dump(mode='json'))
                await self.job_service.save_job(job)

        job['status'] = ExploreJobStatus.DONE.value
        await self.job_service.save_job(job)



