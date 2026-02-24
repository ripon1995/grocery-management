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
        expiry_time = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
        to_encode = {'exp': expiry_time, 'sub': str(subject), 'type': 'refresh'}
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    @staticmethod
    def verify_token(token: str) -> str:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            print(payload)
            user_id: str = payload.get('sub')
            return user_id
        except jwt.ExpiredSignatureError:
            raise UnauthorizedException()
        except jwt.InvalidTokenError:
            raise UnauthorizedException()
