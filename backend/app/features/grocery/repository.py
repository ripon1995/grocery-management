"""
TALKS TO DB ONLY
No FASTAPI no HTTP concepts
"""

from uuid import UUID

from sqlalchemy import select, update, Sequence, and_, or_, cast, String
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ResourceNotFoundException
from app.features.grocery.filters import GroceryFilterParams
from app.features.grocery.models import Grocery


class GroceryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_groceries(self, filters: GroceryFilterParams | None = None) -> Sequence[Grocery]:
        """Get all groceries, optionally filtered/searched — no pagination for now"""
        stmt = select(Grocery)

        if not filters:
            result = await self.session.execute(stmt)
            return result.scalars().all()

        if filters.has_conditions():
            stmt = stmt.where(self._build_filter_conditions(filters))

        if filters.search:
            stmt = stmt.where(self._build_search_conditions(filters.search))

        result = await self.session.execute(stmt)
        return result.scalars().all()

    @staticmethod
    def _build_filter_conditions(filters: GroceryFilterParams):
        filter_fields = ["type", "current_seller", "best_seller", "category", "should_include"]
        conditions = [
            getattr(Grocery, field) == getattr(filters, field)
            for field in filter_fields
            if getattr(filters, field) is not None
        ]
        return and_(*conditions)

    @staticmethod
    def _build_search_conditions(search: str):
        term = f"%{search}%"
        text_fields = [Grocery.name, Grocery.brand]
        cast_fields = [
            Grocery.type, Grocery.current_seller, Grocery.best_seller, Grocery.category,
            Grocery.current_price, Grocery.quantity_in_stock, Grocery.low_stock_threshold, Grocery.best_price,
        ]
        search_conditions = (
            [field.ilike(term) for field in text_fields]
            + [cast(field, String).ilike(term) for field in cast_fields]
        )
        return or_(*search_conditions)

    async def get_by_id(self, grocery_id: str) -> Grocery | None:
        try:
            stmt = select(Grocery).where(Grocery.id == grocery_id)
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()
        except :
            raise ResourceNotFoundException(f"Grocery not found")

    async def add_grocery(self, grocery: Grocery) -> Grocery:
        self.session.add(grocery)
        await self.session.commit()
        return grocery

    async def update_grocery(self, grocery: Grocery) -> Grocery:
        await self.session.commit()
        await self.session.refresh(grocery)
        return grocery

    async def delete_grocery(self, grocery: Grocery) -> None:
        await self.session.delete(grocery)
        await self.session.commit()

    async def bulk_update_should_include(
            self, grocery_ids: Sequence[UUID], should_include: bool
    ) -> Sequence[Grocery]:
        stmt = (
            update(Grocery)
            .where(Grocery.id.in_(grocery_ids))
            .values(should_include=should_include)
            .returning(Grocery)
        )
        result = await self.session.execute(stmt)
        updated_groceries = result.scalars().all()
        await self.session.commit()
        return updated_groceries
