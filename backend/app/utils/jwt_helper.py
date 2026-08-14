import jwt
from datetime import datetime, timedelta, timezone

from app.core.config import settings
from app.core.exceptions import UnauthorizedException


class JWTHelper:
    @staticmethod
    def create_access_token(subject: str) -> str:
        expiry_time = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode = {'exp': expiry_time, 'sub': str(subject), 'type': 'access'}
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    @staticmethod
    def create_refresh_token(subject: str) -> str:
        expiry_time = datetime.now(timezone.utc) + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
        to_encode = {'exp': expiry_time, 'sub': str(subject), 'type': 'refresh'}
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    @staticmethod
    def verify_token(token: str) -> str | None:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            email: str = payload.get('sub')
            return email
        except jwt.ExpiredSignatureError as e:
            raise UnauthorizedException(message='Session expired, please login again') from e
        except jwt.InvalidTokenError as e:
            raise UnauthorizedException(message='Invalid token, please login again') from e
