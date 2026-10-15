"""
DB structure only
"""
import uuid
from datetime import date, datetime

from sqlalchemy import (
    String, Integer, Text, Date, DateTime, ForeignKey, Index,
    Enum as SQLEnum,
    func, text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.common.enums import Seller, PriceSource
from app.db.base import Base
from app.db.mixins import BaseModelMixin


class PriceObservation(Base, BaseModelMixin):
    """One row for every price seen anywhere (manual entry, Gemini, campaign)."""
    __tablename__ = "price_observation"
    __table_args__ = (
        # best price lookup: latest observations of one grocery
        Index(
            "ix_price_observation_grocery_id_observed_at",
            "grocery_id",
            text("observed_at DESC"),
        ),
    )

    grocery_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("grocery.id", ondelete="CASCADE"),
        nullable=False
    )
    seller: Mapped[Seller] = mapped_column(
        SQLEnum(Seller),
        nullable=False
    )
    price: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    source: Mapped[PriceSource] = mapped_column(
        SQLEnum(PriceSource),
        nullable=False
    )
    # required when source is not manual
    source_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )
    # when the price was seen, not when the row was inserted
    observed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )


class Campaign(Base, BaseModelMixin):
    """A campaign running at one of the market shops, collected by the crawler."""
    __tablename__ = "campaign"

    seller: Mapped[Seller] = mapped_column(
        SQLEnum(Seller),
        nullable=False,
        index=True
    )
    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )
    # null for shop-wide campaigns
    product_name: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True
    )
    # as written on the site, e.g. "Buy 1 Get 1"
    discount_text: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )
    discount_percent: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )
    campaign_price: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )
    valid_until: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
        index=True
    )
    source_url: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )
    # hash of seller + title + product + discount, so a re-crawl never duplicates a campaign
    content_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        unique=True
    )
    matched_grocery_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("grocery.id", ondelete="SET NULL"),
        nullable=True
    )
