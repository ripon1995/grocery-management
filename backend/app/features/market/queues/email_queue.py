import logging

from aio_pika.abc import AbstractRobustChannel

logger = logging.getLogger(__name__)

EMAIL_JOB_QUEUE = "email.jobs"


async def declare_email_queue(channel: AbstractRobustChannel) -> None:
    """Declares the email job queue."""
    logger.info("🐇 [RABBITMQ] Declaring EMAIL service queue...")

    await channel.declare_queue(EMAIL_JOB_QUEUE, durable=True)

    logger.info(f"🐇 [RABBITMQ] Queue '{EMAIL_JOB_QUEUE}' declared successfully.")
