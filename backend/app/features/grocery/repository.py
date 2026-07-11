"""
TALKS TO DB ONLY
No FASTAPI no HTTP concepts
"""

from sqlalchemy import select, Sequence, and_, or_, cast, String
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

        if filters:
            if filters.has_conditions():
                conditions = []
                if filters.type is not None:
                    conditions.append(Grocery.type == filters.type)
                if filters.current_seller is not None:
                    conditions.append(Grocery.current_seller == filters.current_seller)
                if filters.best_seller is not None:
                    conditions.append(Grocery.best_seller == filters.best_seller)
                if filters.category is not None:
                    conditions.append(Grocery.category == filters.category)
                if filters.should_include is not None:
                    conditions.append(Grocery.should_include == filters.should_include)
                stmt = stmt.where(and_(*conditions))

            if filters.search:
                term = f"%{filters.search}%"
                stmt = stmt.where(
                    or_(
                        Grocery.name.ilike(term),
                        Grocery.brand.ilike(term),
                        cast(Grocery.type, String).ilike(term),
                        cast(Grocery.current_seller, String).ilike(term),
                        cast(Grocery.best_seller, String).ilike(term),
                        cast(Grocery.category, String).ilike(term),
                        cast(Grocery.current_price, String).ilike(term),
                        cast(Grocery.quantity_in_stock, String).ilike(term),
                        cast(Grocery.low_stock_threshold, String).ilike(term),
                        cast(Grocery.best_price, String).ilike(term),
                    )
                )

        result = await self.session.execute(stmt)
        return result.scalars().all()

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
