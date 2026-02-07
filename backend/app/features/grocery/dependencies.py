"""
dependencies.py (feature scoped)

Feature-specific DI:
	•	permission checks
	•	feature-specific dependencies
"""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.features.grocery.repository import GroceryRepository  # adjust path
from app.features.grocery.service import GroceryService


def get_grocery_repository(db: AsyncSession = Depends(get_db)):
    return GroceryRepository(db)


def get_grocery_service(repo: GroceryRepository = Depends(get_grocery_repository)):
    return GroceryService(repo)
