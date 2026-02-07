"""
DB structure only
"""

from sqlalchemy import (
    String, Boolean, Integer, Float,
    Enum as SQLEnum,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.common.enums import GroceryType, Seller
from app.db.base import Base
from app.db.mixins import BaseModelMixin


class Grocery(Base, BaseModelMixin):
    __tablename__ = "grocery"

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    brand: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    type: Mapped[GroceryType] = mapped_column(
        SQLEnum(GroceryType),
        default=GroceryType.CAN,
        nullable=False
    )
    current_price: Mapped[float] = mapped_column(
        Float(precision=2),
        nullable=False
    )
    current_seller: Mapped[Seller] = mapped_column(
        SQLEnum(Seller),
        default=Seller.MEENA,
        nullable=False
    )
    low_stock_threshold: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    quantity_in_stock: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    should_include: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )
    # computed field
    # following field will be computed everytime when an instance is created
    # or updated
    best_seller: Mapped[Seller] = mapped_column(
        SQLEnum(Seller),
        nullable=False,
        default=Seller.DEFAULT
    )
    best_price: Mapped[float] = mapped_column(
        Float(precision=2),
        nullable=True,
        default=0.0
    )
