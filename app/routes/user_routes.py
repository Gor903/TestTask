from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_async_session
from app.schemas import (
    RefreshRequest,
    UserRequest,
    UserResponse,
    LoginResponse,
    UserUpdate,
)
from app.crud import (
    create_user,
    get_user_by_email,
    get_user_by_code,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
    update_user,
)
from app.dependencies import (
    db_dependency,
    user_dependency,
)

router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    path="/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_new_user(
    user: UserRequest, db: AsyncSession = db_dependency
):
    user_data = user.model_dump()
    user_data["password"] = user_data["password"].get_secret_value()
    db_user = await get_user_by_email(db, user_data["email"])
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken"
        )
    response = await create_user(db, user_data)

    user = await get_user_by_code(
        db=db,
        code=response.code,
    )

    return user


@router.post(
    path="/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
)
async def login_user(
    user: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = db_dependency,
):
    email = user.username
    db_user = await get_user_by_email(db, email)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    res = await verify_password(
        plain_password=user.password, hashed_password=db_user.password_hash
    )
    if not res:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    access_token = await create_access_token(
        user_code=str(db_user.code),
    )
    refresh_token = await create_refresh_token(user_code=str(db_user.code))

    user_update = UserUpdate(
        refresh_token=refresh_token,
    )
    await update_user(
        db=db,
        user_code=db_user.code,
        user=user_update,
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post(
    path="/refresh",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
)
async def refresh_token(
    token: RefreshRequest,
    db: AsyncSession = db_dependency,
):
    is_valid = await verify_refresh_token(
        token=token.refresh_token,
    )
    if not is_valid[0]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=is_valid[1],
        )

    code = is_valid[1]

    db_user = await get_user_by_code(db, code)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect refresh token",
        )

    if not db_user.refresh_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User has not refresh token",
        )

    access_token = await create_access_token(
        user_code=str(code),
    )

    return {
        "access_token": access_token,
        "refresh_token": db_user.refresh_token,
        "token_type": "bearer",
    }


@router.post(
    path="/logout",
    response_model=None,
    status_code=status.HTTP_200_OK,
)
async def logout_user(
    user: user_dependency,
    db: AsyncSession = db_dependency,
):
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    user_update = UserUpdate(
        refresh_token="_",
    )
    await update_user(
        db=db,
        user_code=user.code,
        user=user_update,
    )


@router.get(
    path="/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
)
async def get_me(
    user: user_dependency,
    db: AsyncSession = db_dependency,
):
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user
