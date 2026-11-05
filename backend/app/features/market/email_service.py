import asyncio
from faker import Faker
from app.features.market.schemas.response_schemas import EmailResponseSchema


class EmailService:
    def __init__(self) -> None:
        self.fake = Faker()
        self.mail_to = self.fake.email()
        self.subject = self.fake.sentence(nb_words=6)
        self.body = self.fake.sentence(nb_words=30)

    async def send_email(self) -> EmailResponseSchema:
        await asyncio.sleep(10)
        return EmailResponseSchema(
            mail_to=self.mail_to,
            subject=self.subject,
            body=self.body
        )
