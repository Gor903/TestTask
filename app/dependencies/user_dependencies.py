from typing import Annotated

import jwt
from dotenv import load_dotenv
import os

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.users import get_user_by_code
from app.db import get_async_session

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: AsyncSession = Depends(get_async_session),
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        code = payload.get("sub")
        if not code:
            raise Exception("Invalid token")
        user = await get_user_by_code(code=code, db=db)
        return user
    except Exception as e:
        print(e)
        return None


user_dependency = Annotated[dict, Depends(get_current_user)]
