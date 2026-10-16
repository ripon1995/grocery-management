"""
TALKS TO DB ONLY
No FASTAPI no HTTP concepts
"""

from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.errors import handle_db_errors
from app.features.grocery.models import Grocery


class MarketRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    @handle_db_errors('Failed to fetch groceries from database')
    async def get_groceries_by_ids(self, grocery_ids: Sequence[UUID]) -> Sequence[Grocery]:
        """Fetch groceries whose ID is in grocery_ids. Missing IDs are skipped, order is not guaranteed."""
        stmt = select(Grocery).where(Grocery.id.in_(grocery_ids))
        result = await self.session.execute(stmt)
        return result.scalars().all()
