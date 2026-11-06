import logging
import asyncio

from app.clients.gemini_client import init_gemini_client, get_gemini_client
from app.clients.rabbitmq_client import init_rabbitmq_client, get_rabbitmq_channel
from app.features.market.queues.explore_queue import declare_explore_queue
from app.clients.redis_client import init_redis, get_redis
from app.core.config import settings
from app.core.log_config import configure_logging
from app.services.redis_service import RedisService
from app.worker.email_consumer import EmailJobConsumer
from app.worker.explore_consumer import ExploreJobConsumer
from app.features.market.job_queue_service import MarketJobQueueService
from app.features.market.market_explorer import MarketExplorer
from app.features.market.email_service import EmailService
from app.features.market.queues.email_queue import declare_email_queue

logger = logging.getLogger(__name__)


class Worker:
    def __init__(self):
        self.stop_event = asyncio.Event()

    async def run(self) -> None:
        configure_logging(level=settings.LOG_LEVEL, environment=settings.ENVIRONMENT)
        await init_redis()  # same order as main.py: the fake Gemini needs Redis
        await init_gemini_client()
        await init_rabbitmq_client()

        channel = get_rabbitmq_channel()
        await declare_explore_queue(channel)
        await declare_email_queue(channel)

        job_service = MarketJobQueueService(channel, RedisService(get_redis()))
        consumers = [
            ExploreJobConsumer(
                channel=channel,
                job_service=job_service,
                explorer=MarketExplorer(get_gemini_client())
            ),
            EmailJobConsumer(
                channel=channel,
                job_service=job_service,
                email_service=EmailService()
            ),
        ]

        for consumer in consumers:
            await consumer.start()
        logger.info("⚙️ [WORKER] waiting for explore jobs")
        await self.stop_event.wait()  # ⚠️ CLUE 7: nothing ever sets it


if __name__ == '__main__':
    asyncio.run(Worker().run())
