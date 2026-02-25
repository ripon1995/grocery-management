import logging

from app.core.exceptions import ConflictException, UnauthorizedException
from app.features.auth.models import User
from app.features.auth.repository import AuthRepository
from app.features.auth.schemas import (
    UserCreateRequestSchema,
    UserCreateResponseSchema,
    LoginRequestSchema,
    LoginResponseSchema,
    TokenRefreshRequestSchema,
    TokenRefreshResponseSchema,
)
from app.utils.hashing import hash_password, verify_password
from app.utils.jwt_helper import JWTHelper

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

    @staticmethod
    def __prepare_token(email: str) -> LoginResponseSchema:
        access_token = JWTHelper.create_access_token(email)
        refresh_token = JWTHelper.create_refresh_token(email)
        data = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user_email": email,
        }
        return LoginResponseSchema.model_validate(data)

    @staticmethod
    def __prepare_refresh_token(email: str) -> TokenRefreshResponseSchema:
        access_token = JWTHelper.create_access_token(email)
        refresh_token = JWTHelper.create_refresh_token(email)
        data = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user_email": email,
        }
        return TokenRefreshResponseSchema.model_validate(data)

    # ───────────────────────────────────────────────
    # API methods
    # ───────────────────────────────────────────────

    async def register_user(self, payload: UserCreateRequestSchema) -> UserCreateResponseSchema:
        """User registration api"""
        existing_user = await self.repo.get_user_by_email(payload.email)
        if existing_user:
            # through error
            logger.debug('User already exists')
            raise ConflictException(message='User already exists')

        hashed_password = hash_password(payload.password)
        user = self.__prepare_user(payload, hashed_password)
        created_user = await self.repo.create_user(user)
        return UserCreateResponseSchema.model_validate(created_user)

    async def authenticate_user(self, payload: LoginRequestSchema) -> LoginResponseSchema:
        """User login api"""
        user = await self.repo.get_user_by_email(payload.email)
        if not user or not verify_password(payload.password, user.password):
            raise UnauthorizedException()

        return self.__prepare_token(user.email)

    async def refresh_token(self, payload: TokenRefreshRequestSchema) -> TokenRefreshResponseSchema:
        """
        Validate old refresh token and issue new access + refresh tokens.
        Uses token rotation (new refresh token each time).
        """
        email = JWTHelper.verify_token(payload.refresh_token)
        if not email:
            raise UnauthorizedException()
        user = self.repo.get_user_by_email(email)
        if not user:
            raise UnauthorizedException()

        return self.__prepare_refresh_token(email)
