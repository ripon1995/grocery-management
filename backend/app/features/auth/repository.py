from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.auth.models import User


class AuthRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_by_email(self, email: str):
        stmt = select(User).where(User.email == email)
        result = await self.session.execute(stmt)
        return result.scalars().one_or_none()

    async def create_user(self, user: User) -> User:
        self.session.add(user)
        await self.session.commit()
        return user
