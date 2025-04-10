from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import ForeignKey, Integer, String, Column, Text
from sqlalchemy import UUID as sqlalchemy_UUID
from app.db.database import Base

if TYPE_CHECKING:
    from app.db.models.users import User


class Room(Base):
    __tablename__ = "room"

    code: Mapped[UUID] = Column(
        sqlalchemy_UUID,
        default=uuid4,
        primary_key=True,
        unique=True,
        nullable=False,
    )

    name: Mapped[str] = Column(
        String(64),
        nullable=False,
        unique=True,
    )

    sit_count: Mapped[int] = Column(
        Integer,
        nullable=False,
    )

    schedules: Mapped[list["Schedule"]] = relationship(
        "Schedule",
        back_populates="room",
        cascade="all, delete",
        lazy="select",
    )


class Presentation(Base):
    __tablename__ = "presentation"

    code: Mapped[UUID] = mapped_column(
        sqlalchemy_UUID,
        unique=True,
        default=uuid4,
        nullable=False,
        primary_key=True,
    )

    title: Mapped[str] = Column(
        String(64),
        nullable=False,
    )

    description: Mapped[Text] = Column(
        Text,
        nullable=False,
    )

    users: Mapped[list["PresentationPresenter"]] = relationship(
        "PresentationPresenter",
        back_populates="presentation",
        # cascade="all, delete",
        lazy="select",
    )

    schedule: Mapped["Schedule"] = relationship(
        "Schedule",
        back_populates="presentation",
        # cascade="all, delete",
        lazy="select",
    )


class PresentationPresenter(Base):
    __tablename__ = "presentation_presenters"

    presentation_code: Mapped[UUID] = mapped_column(
        sqlalchemy_UUID,
        ForeignKey(
            "presentation.code",
            ondelete="CASCADE",
        ),
        primary_key=True,
        nullable=False,
    )
    user_code: Mapped[UUID] = mapped_column(
        sqlalchemy_UUID,
        ForeignKey(
            "user.code",
            ondelete="CASCADE",
        ),
        primary_key=True,
        nullable=False,
    )

    presentation: Mapped["Presentation"] = relationship(
        "Presentation",
        foreign_keys=[presentation_code],
        back_populates="users",
        lazy="select",
    )
    user: Mapped["User"] = relationship(
        "User",
        foreign_keys=[user_code],
        back_populates="presentations",
        lazy="select",
    )


class Schedule(Base):
    __tablename__ = "schedules"

    code: Mapped[UUID] = mapped_column(
        sqlalchemy_UUID,
        unique=True,
        default=uuid4,
        nullable=False,
    )

    room_code: Mapped[UUID] = mapped_column(
        sqlalchemy_UUID,
        ForeignKey(
            "room.code",
            ondelete="CASCADE",
        ),
        primary_key=True,
        nullable=False,
    )

    presentation_code: Mapped[UUID] = mapped_column(
        sqlalchemy_UUID,
        ForeignKey(
            "presentation.code",
            ondelete="CASCADE",
        ),
        primary_key=True,
        nullable=False,
    )

    start_time: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
    )

    end_time: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
    )

    room: Mapped[Room] = relationship(
        "Room",
        foreign_keys=[room_code],
        back_populates="schedules",
        lazy="select",
    )

    presentation: Mapped[Presentation] = relationship(
        "Presentation",
        foreign_keys=[presentation_code],
        back_populates="schedule",
        lazy="select",
    )
