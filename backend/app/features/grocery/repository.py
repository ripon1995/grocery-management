"""
TALKS TO DB ONLY
No FASTAPI no HTTP concepts
"""

from sqlalchemy import select, Sequence
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.grocery.models import Grocery


class GroceryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_groceries(self) -> Sequence[Grocery]:
        """Get all groceries — no pagination for now"""
        stmt = select(Grocery)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_id(self, grocery_id: str) -> Grocery | None:
        stmt = select(Grocery).where(Grocery.id == grocery_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def add_grocery(self, grocery: Grocery) -> Grocery:
        self.session.add(grocery)
        await self.session.commit()
        return grocery

    async def update_grocery(self, grocery: Grocery) -> Grocery:
        await self.session.commit()
        await self.session.refresh(grocery)
        return grocery
