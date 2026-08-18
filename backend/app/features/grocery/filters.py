"""
filters.py (feature scoped)

Plain data holder for list-endpoint filter/search query params.
Kept free of FastAPI/pydantic so the repository layer can consume it
without importing the HTTP or schema layers.
"""

from dataclasses import dataclass
from typing import Optional

from app.common.enums import GroceryType, Seller, GroceryCategory


@dataclass
class GroceryFilterParams:
    type: Optional[GroceryType] = None
    current_seller: Optional[Seller] = None
    best_seller: Optional[Seller] = None
    category: Optional[GroceryCategory] = None
    should_include: Optional[bool] = None
    search: Optional[str] = None

    def has_conditions(self) -> bool:
        return any(
            value is not None
            for value in [self.type, self.current_seller, self.best_seller, self.category, self.should_include]
        )
