from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import get_user_by_code
from app.db.database import get_async_session
from app.dependencies import get_current_user
from app.routes.user_routes import oauth2_scheme

from app.schemas import (
    PresentationRequest,
    PresentationResponse,
)

from app.crud.events import (
    create_presentation,
    get_presentation,
)

router = APIRouter(prefix="/events", tags=["Events"])


@router.post(
    path="/presentation/create",
    response_model=PresentationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def presentation_create(
    presentation: PresentationRequest,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_async_session),
):
    code = await get_current_user(token)
    if not code:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token Expired",
        )
    user = await get_user_by_code(
        db=db,
        code=code,
    )
    if not user or user.role == "listener":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect request",
        )

    presentation = await create_presentation(
        db=db,
        presentation=presentation.model_dump(),
    )
    if not presentation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Wrong input",
        )

    presentation = await get_presentation(
        code=presentation.code,
        db=db,
    )

    return presentation
