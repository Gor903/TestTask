import bcrypt
import jwt
from datetime import datetime, timedelta
from typing import Tuple
import asyncio

from sqlalchemy.ext.asyncio import AsyncSession

SECRET_KEY = "your_secret_key"
REFRESH_SECRET_KEY = "your_refresh_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7


async def hash_password(password: str) -> str:
    hashed = await asyncio.to_thread(
        bcrypt.hashpw,
        password.encode(),
        bcrypt.gensalt(),
    )

    return hashed.decode()


async def verify_password(plain_password: str, hashed_password: str) -> bool:
    is_valid = await asyncio.to_thread(
        bcrypt.checkpw,
        plain_password.encode(),
        hashed_password.encode(),
    )

    return is_valid


# TODO: create access token with more data
async def create_access_token(user_code: str) -> str:
    expiration_time = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {
        "sub": user_code,
        "exp": expiration_time,
    }

    token = await asyncio.to_thread(
        jwt.encode,
        payload,
        SECRET_KEY,
        ALGORITHM,
    )

    return token


# TODO: create refresh token with more data
async def create_refresh_token(user_code: str) -> str:
    expiration_time = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    payload = {"sub": user_code, "exp": expiration_time}

    refresh_token = await asyncio.to_thread(
        jwt.encode,
        payload,
        SECRET_KEY,
        ALGORITHM,
    )

    return refresh_token


async def verify_access_token(token: str) -> Tuple[bool, str]:
    try:
        decoded_token = await asyncio.to_thread(
            jwt.decode, token, SECRET_KEY, algorithms=["HS256"]
        )
        return True, decoded_token["sub"]
    except jwt.ExpiredSignatureError:
        return False, "Token has expired"
    except jwt.InvalidTokenError:
        return False, "Invalid token"


async def verify_refresh_token(token: str) -> Tuple[bool, str]:
    try:
        decoded_token = await asyncio.to_thread(
            jwt.decode,
            token,
            SECRET_KEY,
            [ALGORITHM],
        )

        return True, decoded_token["sub"]
    except jwt.ExpiredSignatureError:
        return False, "Refresh token has expired"
    except jwt.InvalidTokenError:
        return False, "Invalid refresh token"
