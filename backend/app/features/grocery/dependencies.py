"""
dependencies.py (feature scoped)

Feature-specific DI:
	•	permission checks
	•	feature-specific dependencies
"""

from typing import Optional

from fastapi import Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.enums import GroceryType, Seller, GroceryCategory
from app.db.session import get_db
from app.features.grocery.filters import GroceryFilterParams
from app.features.grocery.repository import GroceryRepository  # adjust path
from app.features.grocery.service import GroceryService


def get_grocery_repository(db: AsyncSession = Depends(get_db)):
    return GroceryRepository(db)


def get_grocery_service(repo: GroceryRepository = Depends(get_grocery_repository)):
    return GroceryService(repo)


def get_grocery_filters(
        type: Optional[GroceryType] = Query(default=None, description="Filter by grocery type"),
        current_seller: Optional[Seller] = Query(default=None, description="Filter by current seller"),
        best_seller: Optional[Seller] = Query(default=None, description="Filter by best seller"),
        category: Optional[GroceryCategory] = Query(default=None, description="Filter by category"),
        should_include: Optional[bool] = Query(default=None, description="Filter by should-include flag"),
        search: Optional[str] = Query(default=None, min_length=1, description="Free text search across fields"),
) -> GroceryFilterParams:
    return GroceryFilterParams(
        type=type,
        current_seller=current_seller,
        best_seller=best_seller,
        category=category,
        should_include=should_include,
        search=search,
    )
