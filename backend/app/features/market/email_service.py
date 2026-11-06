import logging
import asyncio
from faker import Faker
from app.features.market.schemas.response_schemas import EmailResponseSchema

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self) -> None:
        self.fake = Faker()

    async def send_email(self) -> EmailResponseSchema:
        await asyncio.sleep(30)
        mail_to = self.fake.email()
        subject = self.fake.sentence(nb_words=6)
        body = self.fake.sentence(nb_words=30)
        logger.debug(f"Sending email to {mail_to}")
        return EmailResponseSchema(
            mail_to=mail_to,
            subject=subject,
            body=body
        )
