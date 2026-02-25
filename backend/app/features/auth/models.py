from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

from app.db.mixins import BaseModelMixin


class User(Base, BaseModelMixin):
    __tablename__ = "user"

    username: Mapped[str] = mapped_column(
        String(30),
        unique=True,
        nullable=False
    )
    email: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False
    )
    password: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    def __repr__(self):
        return f"<User {self.username}> {self.email}> is created."
