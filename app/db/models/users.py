from uuid import UUID, uuid4

from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import Integer, String, Column
from app.db.database import Base

class User(Base):
    __tablename__ = "users"

    code: Mapped[UUID] = mapped_column(
        unique = True,
        default = uuid4,
        nullable = False,
        primary_key = True,
    )

    first_name: Mapped[str] = mapped_column(
        String(255),
        nullable = False,
    )

    last_name: Mapped[str] = mapped_column(
        String(255),
        nullable = False,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        nullable = False,
        unique = True,
        index = True,
    )

    password_hash: Mapped[str] = mapped_column(
        String(255), nullable = False, index = True
        # length depends on hash algorythm
    )
