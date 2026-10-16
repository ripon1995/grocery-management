import logging
from urllib.parse import urlsplit

import aio_pika
from aio_pika.abc import (
    AbstractRobustConnection,
    AbstractRobustChannel
)
from app.common.constants import EXPLORE_JOBS_QUEUE
from app.core.config import settings

logger = logging.getLogger(__name__)

rabbitmq_connection: AbstractRobustConnection | None = None
rabbitmq_channel: AbstractRobustChannel | None = None


async def init_rabbitmq_client() -> None:
    global rabbitmq_connection, rabbitmq_channel
    url = urlsplit(settings.RABBIT_MQ_CONNECTION_URL)  # log host:port only, never the credentials
    logger.info(f"🐇 [RABBITMQ] connecting to {url.hostname}:{url.port}")
    try:
        rabbitmq_connection = await aio_pika.connect_robust(settings.RABBIT_MQ_CONNECTION_URL)
        rabbitmq_channel = await rabbitmq_connection.channel()  # publisher confirms on by default
        # durable: the queue (and its persistent messages) survive a broker restart
        await rabbitmq_channel.declare_queue(EXPLORE_JOBS_QUEUE, durable=True)
    except Exception as e:
        logger.error(f"🐇 [RABBITMQ] connection to {url.hostname}:{url.port} failed: {e!r}")
        raise
    logger.info(f"🐇 [RABBITMQ] connected to {url.hostname}:{url.port}")


async def close_rabbitmq_client() -> None:
    global rabbitmq_connection, rabbitmq_channel
    if rabbitmq_channel and not rabbitmq_channel.is_closed:
        await rabbitmq_channel.close()
    if rabbitmq_connection and not rabbitmq_connection.is_closed:
        await rabbitmq_connection.close()

    rabbitmq_channel = None
    rabbitmq_connection = None
    logger.info("🐇 [RABBITMQ] connection closed")


def get_rabbitmq_channel() -> AbstractRobustChannel:
    if rabbitmq_channel is None or rabbitmq_channel.is_closed:
        raise RuntimeError("RabbitMQ channel is not available")  # also while a robust reconnect is in progress

    return rabbitmq_channel
