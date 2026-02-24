import jwt
from datetime import datetime, timedelta, timezone

from app.core.config import settings

ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 5
REFRESH_TOKEN_EXPIRE_MINUTES = 10


class JWTHelper:
    @staticmethod
    def create_access_token(subject: str) -> str:
        expiry_time = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode = {'exp': expiry_time, 'sub': str(subject), 'type': 'access'}
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)

    @staticmethod
    def create_refresh_token(subject: str) -> str:
        expiry_time = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_MINUTES)
        to_encode = {'exp': expiry_time, 'sub': str(subject), 'type': 'refresh'}
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)

    @staticmethod
    def verify_token(token: str) -> str:
        # TODO => need to implement this later
        print(token)
        return token
