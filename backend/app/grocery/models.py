from typing import Optional
from pydantic import Field, PositiveFloat, AliasChoices

from backend.app.grocery.schemas.grocery_base import GroceryBase


# db model
# talks with database
class Grocery(GroceryBase):
    id: Optional[str] = Field(None, validation_alias=AliasChoices('_id', 'id'))
    # inherits all the fields from grocery base and adds the new fields
    # calculated field
    best_price: Optional[PositiveFloat] = Field(
        default=None,
        description="Lowest price recorded. Defaults to current_price if not provided."
    )
    best_seller: Optional[str] = Field(
        default=None,
        description="Best seller recorded. Defaults to current_price if not provided."
    )
