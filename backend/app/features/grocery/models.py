from app.database.base import Base


# db model
# talks with db
# class Grocery(GroceryBase):
#     id: Optional[str] = Field(None, validation_alias=AliasChoices('_id', 'id'))
#     # inherits all the fields from grocery base and adds the new fields
#     # calculated field
#     best_price: Optional[PositiveFloat] = Field(
#         default=None,
#         description="Lowest price recorded. Defaults to current_price if not provided."
#     )
#     best_seller: Optional[str] = Field(
#         default=None,
#         description="Best seller recorded. Defaults to current_price if not provided."
#     )
#

from sqlalchemy import String, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

class Todo(Base):
    __tablename__ = "todos"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    title: Mapped[str] = mapped_column(String(255), nullable=False)

    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
