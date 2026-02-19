from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.features.auth.repository import AuthRepository
from app.features.auth.service import AuthService


def get_auth_repository(db: AsyncSession = Depends(get_db)):
    return AuthRepository(db)


def get_auth_service(repo: AuthRepository = Depends(get_auth_repository)):
    return AuthService(repo)
