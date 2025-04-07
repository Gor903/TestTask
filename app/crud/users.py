from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import User
from .auth import hash_password
from app.schemas import UserUpdate
from sqlalchemy.exc import IntegrityError


async def get_user_by_email(db: AsyncSession, email: str):
    query = select(User).where(User.email == email)
    user = await db.scalar(query)
    return user


async def get_user_by_code(db: AsyncSession, code: str):
    query = select(User).where(User.code == code)
    user = await db.scalar(query)
    return user


async def create_user(db: AsyncSession, user: dict) -> User:
    hashed_password = await hash_password(user.get("password"))
    try:
        db_user = User(
            first_name=user.get("first_name"),
            last_name=user.get("last_name"),
            email=user.get("email"),
            password_hash=hashed_password,
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
    if db_user:
        # TODO: update "genericly"
        if user.first_name:
            db_user.first_name = user.first_name
        if user.last_name:
            db_user.last_name = user.last_name
        if user.email:
            db_user.email = user.email
        if user.password:
            hashed_password = await hash_password(user.password.get_secret_value())
            db_user.password_hash = hashed_password
        if user.refresh_token:
            db_user.refresh_token = user.refresh_token

        await db.commit()
        return db_user
    return None
