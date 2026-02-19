import logging

from app.core.exceptions import ConflictException
from app.features.auth.models import User
from app.features.auth.repository import AuthRepository
from app.features.auth.schemas import UserCreateRequestSchema, UserCreateResponseSchema
from app.utils.hashing import hash_password

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(self, repo: AuthRepository):
        self.repo = repo

    # ───────────────────────────────────────────────
    # Prepare / mapping methods
    # ───────────────────────────────────────────────
    @staticmethod
    def __prepare_user(payload: UserCreateRequestSchema, hashed_password) -> User:
        values = payload.model_dump()
        values['password'] = hashed_password
        return User(**values)

    # ───────────────────────────────────────────────
    # API methods
    # ───────────────────────────────────────────────

    async def register_user(self, payload: UserCreateRequestSchema) -> UserCreateResponseSchema:
        existing_user = await self.repo.get_user_by_email(payload.email)
        if existing_user:
            # through error
            logger.debug('User already exists')
            raise ConflictException(message='User already exists')

        hashed_password = hash_password(payload.password)
        user = self.__prepare_user(payload, hashed_password)
        created_user = await self.repo.create_user(user)
        return UserCreateResponseSchema.model_validate(created_user)
