import aio_pika
from aio_pika.abc import (
    AbstractRobustConnection,
    AbstractRobustChannel
)
from app.core.config import settings

rabbitmq_connection: AbstractRobustConnection | None = None
rabbitmq_channel: AbstractRobustChannel | None = None


async def init_rabbitmq_client() -> None:
    global rabbitmq_connection, rabbitmq_channel
    rabbitmq_connection = await aio_pika.connect_robust(settings.RABBIT_MQ_CONNECTION_URL)
    rabbitmq_channel = await rabbitmq_connection.channel()


async def close_rabbitmq_client() -> None:
    global rabbitmq_connection, rabbitmq_channel
    if rabbitmq_channel and not rabbitmq_channel.is_closed:
        await rabbitmq_channel.close()
    if rabbitmq_connection and not rabbitmq_connection.is_closed:
        await rabbitmq_connection.close()

    rabbitmq_channel = None
    rabbitmq_connection = None



def get_rabbitmq_channel() -> AbstractRobustChannel:
    if rabbitmq_channel is None or rabbitmq_channel.is_closed:
        raise RuntimeError("RabbitMQ connection not initialized")

    return rabbitmq_channel
