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
        return any([
            self.type is not None,
            self.current_seller is not None,
            self.best_seller is not None,
            self.category is not None,
            self.should_include is not None,
        ])
