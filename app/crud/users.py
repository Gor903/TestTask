from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import User
from .auth import hash_password
from app.schemas import UserUpdate
from sqlalchemy.exc import IntegrityError


async def get_user_by_email(db: AsyncSession, email: str):
    query = select(User).where(User.email == email)
    user = await db.scalar(query)
    return user


async def get_user_by_code(db: AsyncSession, code: str):
    stmt = (
        select(User).options(selectinload(User.presentations)).where(User.code == code)
    )

    res = await db.execute(stmt)

    user = res.scalar_one_or_none()

    return user


async def create_user(db: AsyncSession, user: dict) -> User:
    hashed_password = await hash_password(user.get("password"))
    try:
        db_user = User(
            first_name=user.get("first_name"),
            last_name=user.get("last_name"),
            email=user.get("email"),
            password_hash=hashed_password,
            role=user.get("role"),
        )
        db.add(db_user)
        await db.commit()
        return db_user
    except IntegrityError:
        # TODO change to HTTPException
        raise ValueError("Username or email already exists")
    except Exception as error:
        # TODO change to HTTPException
        raise ValueError(f"Error: {error}")


async def update_user(db: AsyncSession, user_code: str, user: UserUpdate):
    db_user = await get_user_by_code(db, user_code)
    user = user.model_dump(exclude_none = True)
    if db_user:

        for i, v in user.items():
            setattr(db_user, i, v)

        await db.commit()
        return db_user
    return None
