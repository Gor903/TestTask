import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_async_session
from app.dependencies import (
    user_dependency,
)

from app.schemas import (
    PresentationRequest,
    PresentationResponse,
    RoomRequest,
    RoomResponse,
)

from app.crud.events import (
    create_presentation,
    get_presentation,
    create_room,
    get_presentations,
    get_room,
    get_rooms,
)

router = APIRouter(prefix="/events", tags=["Events"])


@router.post(
    path="/presentation/create",
    response_model=PresentationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def presentation_create(
    presentation: PresentationRequest,
    user: user_dependency,
    db: AsyncSession = Depends(get_async_session),
):
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


@router.post(
    path="/room/create",
    response_model=RoomResponse,
    status_code=status.HTTP_201_CREATED,
)
async def room_create(
    room: RoomRequest,
    user: user_dependency,
    db: AsyncSession = Depends(get_async_session),
):
    room = await create_room(
        db=db,
        room=room.model_dump(),
    )

    if not room:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Wrong input",
        )

    room = await get_room(
        db=db,
        code=room.code,
    )

    return room


@router.get(
    path="/presentations",
    response_model=List[PresentationResponse],
    status_code=status.HTTP_200_OK,
)
async def presentations_all(
    user: user_dependency,
    db: AsyncSession = Depends(get_async_session),
):
    presentations = await get_presentations(db=db)

    return presentations


@router.get(
    path="/presentations/{presentation_code}",
    response_model=PresentationResponse,
    status_code=status.HTTP_200_OK,
)
async def presentations_all(
    presentation_code: uuid.UUID,
    user: user_dependency,
    db: AsyncSession = Depends(get_async_session),
):
    presentation = await get_presentation(
        db=db,
        code=presentation_code,
    )

    if not presentation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Presentation not found",
        )

    return presentation


@router.get(
    path="/rooms",
    response_model=List[RoomResponse],
    status_code=status.HTTP_200_OK,
)
async def rooms_all(
    user: user_dependency,
    db: AsyncSession = Depends(get_async_session),
):
    rooms = await get_rooms(db=db)

    return rooms


@router.get(
    path="/room/{room_code}",
    response_model=RoomResponse,
    status_code=status.HTTP_200_OK,
)
async def rooms_all(
    room_code: uuid.UUID,
    user: user_dependency,
    db: AsyncSession = Depends(get_async_session),
):
    room = await get_room(
        db=db,
        code=room_code,
    )

    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found",
        )

    return room
