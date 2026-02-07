import uuid
from sqlalchemy import func, DateTime, UUID
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime


class IdMixin:
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=None
    )


class TimestampMixin:
    """Adds created_at / updated_at - auto-managed by database"""
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )


class BaseModelMixin(IdMixin, TimestampMixin):
    pass