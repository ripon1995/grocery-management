import logging
from aio_pika.abc import AbstractRobustChannel

logger = logging.getLogger(__name__)


EXPLORE_JOBS_QUEUE = 'explore.jobs'

async def declare_explore_queue(channel: AbstractRobustChannel) -> None:
    """
        Declares the market feature queues, DLQs, and retry configurations.
        This represents the market feature's contract with the broker.
    """
    logger.info("🐇 [RABBITMQ] Declaring market feature queue topologies...")
    await channel.declare_queue(
        EXPLORE_JOBS_QUEUE,
        durable=True,
    )
    logger.info(f"🐇 [RABBITMQ] Queue '{EXPLORE_JOBS_QUEUE}' declared successfully.")
