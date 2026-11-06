import json
import logging

from aio_pika.abc import AbstractRobustChannel, AbstractIncomingMessage

from app.common.enums import MailJobStatus
from app.features.market.job_queue_service import MarketJobQueueService
from app.features.market.email_service import EmailService
from app.features.market.queues.email_queue import EMAIL_JOB_QUEUE

logger = logging.getLogger(__name__)


class EmailJobConsumer:

    def __init__(
            self,
            channel: AbstractRobustChannel,
            job_service: MarketJobQueueService,
            email_service: EmailService,
    ) -> None:
        self.channel = channel
        self.email_service = email_service
        self.job_service = job_service

    async def start(self) -> None:
        job_queue = await self.channel.get_queue(EMAIL_JOB_QUEUE)
        await job_queue.consume(self.__on_message)

    async def __on_message(self, message: AbstractIncomingMessage) -> None:
        async with message.process(requeue=False):
            body = json.loads(message.body)
            logger.info(f"⚙️ [WORKER] job {body['job_id']} received (redelivered={message.redelivered})")
            await self.__run_job(body['job_id'])

    async def __run_job(self, job_id: str) -> None:
        job = await self.job_service.get_email_job(job_id)
        if job is None:
            logger.info('No EMAIL job found')
            return

        job['status'] = MailJobStatus.SENDING.value
        await self.job_service.save_email_job(job)

        logger.info(f"⚙️ [WORKER] job -> Calling email service to send email)")
        result = await self.email_service.send_email()
        job['result'] = result.model_dump(mode='json')
        job['status'] = MailJobStatus.SENT.value

        await self.job_service.save_email_job(job)
        logger.info(f"⚙️ [WORKER] job {job_id} done  results)")
