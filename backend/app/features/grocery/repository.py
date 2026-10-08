"""
TALKS TO DB ONLY
No FASTAPI no HTTP concepts
"""

from uuid import UUID

from sqlalchemy import select, update, Sequence, and_, or_, cast, String, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.errors import handle_db_errors
from app.features.grocery.filters import GroceryFilterParams
from app.features.grocery.models import Grocery


class GroceryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    # ================================= simulator helpers ==================================
    async def __simulation_database_timeout(self, sleep_time: int) -> None:
        """Simulate database timeout"""
        await self.session.execute(select(func.pg_sleep(sleep_time)))

    # ================================= filter and search methods ==================================
    @staticmethod
    def __build_filter_conditions(filters: GroceryFilterParams):
        filter_fields = ["type", "current_seller", "best_seller", "category", "should_include"]
        conditions = [
            getattr(Grocery, field) == value
            for field in filter_fields
            if (value := getattr(filters, field)) is not None
        ]
        return and_(*conditions)

    @staticmethod
    def __build_search_conditions(search: str):
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


    # ================================= CRUDS ==================================

    @handle_db_errors('Failed to fetch groceries from database')
    async def get_groceries(self, filters: GroceryFilterParams | None = None) -> Sequence[Grocery]:
        """Get all groceries, optionally filtered/searched — no pagination for now"""

        await self.__simulation_database_timeout(10)

        stmt = select(Grocery)

        if not filters:
            result = await self.session.execute(stmt)
            return result.scalars().all()

        if filters.has_conditions():
            stmt = stmt.where(self.__build_filter_conditions(filters))

        if filters.search:
            stmt = stmt.where(self.__build_search_conditions(filters.search))

        result = await self.session.execute(stmt)
        return result.scalars().all()

    @handle_db_errors('Failed to fetch grocery from database')
    async def get_by_id(self, grocery_id: str) -> Grocery | None:
        """Fetch a single grocery item by ID. Returns None if not found."""
        stmt = select(Grocery).where(Grocery.id == grocery_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    @handle_db_errors('Failed to add grocery to database')
    async def add_grocery(self, grocery: Grocery) -> Grocery:
        """Add a new grocery item. Rolls back on error."""
        self.session.add(grocery)
        await self.session.commit()
        await self.session.refresh(grocery)
        return grocery

    @handle_db_errors('Failed to update grocery in database')
    async def update_grocery(self, grocery: Grocery) -> Grocery:
        """Update an existing grocery item. Rolls back on error."""
        await self.session.commit()
        await self.session.refresh(grocery)
        return grocery

    @handle_db_errors('Failed to delete grocery from database')
    async def delete_grocery(self, grocery: Grocery) -> None:
        """Delete a grocery item. Rolls back on error."""
        await self.session.delete(grocery)
        await self.session.commit()

    @handle_db_errors('Failed to bulk update should_include in database')
    async def bulk_update_should_include(
            self, grocery_ids: Sequence[UUID],
            should_include: bool
    ) -> Sequence[Grocery]:
        """Bulk update 'should_include'. Rolls back on error."""
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
