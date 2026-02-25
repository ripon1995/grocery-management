from fastapi import Depends
from jwt import ExpiredSignatureError, InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import UnauthorizedException
from app.core.security import oauth2_scheme
from app.db.session import get_db as _get_db
from app.features.auth.models import User
from app.features.auth.repository import AuthRepository
from app.utils.jwt_helper import JWTHelper

get_db = _get_db


async def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: AsyncSession = Depends(get_db),
) -> User:
    try:
        user_email = JWTHelper.verify_token(token)
        if user_email is None:
            raise UnauthorizedException()
    except (ExpiredSignatureError, InvalidTokenError):
        raise UnauthorizedException()

    # Fetch fresh user from database (recommended)
    user = await AuthRepository(db).get_user_by_email(email=user_email)
    if user is None:
        raise UnauthorizedException()

    return user
