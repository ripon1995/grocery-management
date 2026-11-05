import random
from enum import Enum

from faker import Faker

from app.features.market.schemas.response_schemas import EmailResponseSchema


class MailStatus(Enum):
    PENDING = 'PENDING'
    SENDING = 'SENDING'
    SENT = 'SENT'
    FAILED = 'FAILED'


class EmailService:
    def __init__(self) -> None:
        self.fake = Faker()
        self.mail_to = self.fake.email()
        self.subject = self.fake.sentence(nb_words=6)
        self.body = self.fake.sentence(nb_words=30)
        self.mail_status = MailStatus.PENDING.value

    @staticmethod
    def __parse_mail_status() -> MailStatus:
        return random.choice(list(MailStatus))

    async def send_email(self) -> EmailResponseSchema:
        self.mail_status = self.__parse_mail_status().value
        return EmailResponseSchema(
            mail_to=self.mail_to,
            subject=self.subject,
            body=self.body,
            mail_status=self.mail_status
        )
