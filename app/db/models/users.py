from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import Integer, String, Column, Enum
from app.db.database import Base
from app.db.models.enums import UserRole

if TYPE_CHECKING:
    from app.db.models.events import PresentationPresenter


class User(Base):
    __tablename__ = "user"

    code: Mapped[UUID] = mapped_column(
        unique=True,
        default=uuid4,
        nullable=False,
        primary_key=True,
    )

    first_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    last_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
        # length depends on hash algorythm
    )

    refresh_token: Mapped[str] = mapped_column(
        String(300),
        nullable=True,
    )

    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole),
        nullable=False,
    )

    presentations: Mapped[list["PresentationPresenter"]] = relationship(
        "PresentationPresenter",
        back_populates="user",
        cascade="all, delete",
    )
