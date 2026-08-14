"""
TALKS TO DB ONLY
No FASTAPI no HTTP concepts
"""

from uuid import UUID

from sqlalchemy import select, update, Sequence, and_, or_, cast, String
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import DatabaseException
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
        """Fetch a single grocery item by ID. Returns None if not found."""
        stmt = select(Grocery).where(Grocery.id == grocery_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def add_grocery(self, grocery: Grocery) -> Grocery:
        """Add a new grocery item with explicit transaction rollback on error."""
        try:
            self.session.add(grocery)
            await self.session.commit()
            await self.session.refresh(grocery)
            return grocery
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise DatabaseException('Failed to add grocery from database') from e

    async def update_grocery(self, grocery: Grocery) -> Grocery:
        """Update an existing grocery item with explicit transaction rollback on error."""
        try:
            await self.session.commit()
            await self.session.refresh(grocery)
            return grocery
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise DatabaseException('Failed to update grocery from database') from e

    async def delete_grocery(self, grocery: Grocery) -> None:
        """Delete a grocery item with explicit transaction rollback on error."""
        try:
            await self.session.delete(grocery)
            await self.session.commit()
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise DatabaseException('Failed to delete grocery from database') from e

    async def bulk_update_should_include(
            self, grocery_ids: Sequence[UUID], should_include: bool
    ) -> Sequence[Grocery]:
        """Bulk update 'should_include' with explicit transaction rollback on error."""
        try:
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
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise DatabaseException('Failed to bulk update should_include from database') from e
