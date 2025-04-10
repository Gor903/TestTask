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
    SchedulesRequest,
    SchedulesResponse,
)

from app.crud.events import (
    create_presentation,
    get_presentation,
    create_room,
    get_presentations,
    get_room,
    get_rooms,
    create_schedule,
    get_schedule,
    get_schedules,
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
    if user.role == "listener":
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
    # TODO: Only admin can create Room

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


@router.post(
    path="/schedule/create",
    response_model=SchedulesResponse,
    status_code=status.HTTP_201_CREATED,
)
async def schedule_create(
    schedule: SchedulesRequest,
    user: user_dependency,
    db: AsyncSession = Depends(get_async_session),
):
    if user.role == "listener":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect request",
        )

    schedule = await create_schedule(
        db=db,
        schedule=schedule.model_dump(),
    )

    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Wrong input",
        )

    schedule = await get_schedule(
        db=db,
        code=schedule.code,
    )

    return schedule


@router.get(
    path="/presentations",
    response_model=List[PresentationResponse],
    status_code=status.HTTP_200_OK,
)
async def presentations_all(
    user: user_dependency,
    db: AsyncSession = Depends(get_async_session),
):
    presentations = await get_presentations(db=db, user_code=user.code)

    return presentations


@router.get(
    path="/presentations/{presentation_code}",
    response_model=PresentationResponse,
    status_code=status.HTTP_200_OK,
)
async def presentation_get(
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


@router.get(
    path="/schedules",
    response_model=List[SchedulesResponse],
    status_code=status.HTTP_200_OK,
)
async def schedules_all(
    user: user_dependency,
    db: AsyncSession = Depends(get_async_session),
    room_code: uuid.UUID = None,
    future: bool = False,
):
    schedules = await get_schedules(
        db=db,
        room_code=room_code,
        future=future,
    )

    return schedules


@router.get(
    path="/schedule/{schedule_code}",
    response_model=SchedulesResponse,
    status_code=status.HTTP_200_OK,
)
async def schedule_get(
    code: uuid.UUID,
    user: user_dependency,
    db: AsyncSession = Depends(get_async_session),
):
    schedule = await get_schedule(
        db=db,
        code=code,
    )

    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Schedule not found",
        )

    return schedule


@router.delete(
    path="/presentation/{presentation_code}",
)
async def presentation_delete(
    code: uuid.UUID,
    user: user_dependency,
    db: AsyncSession = Depends(get_async_session),
):
    if not user or user.role == "listener":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect request",
        )

    presentation = await get_presentation(
        db=db,
        code=code,
    )

    if not presentation or not any(
        map(lambda x: user.code == x.user_code, presentation.users)
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to perform this action",
        )

    await db.delete(presentation)
    await db.commit()

    return None


@router.delete(
    path="/schedule/{schedule_code}",
)
async def schedule_delete(
    code: uuid.UUID,
    user: user_dependency,
    db: AsyncSession = Depends(get_async_session),
):
    if not user or user.role == "listener":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect request",
        )

    schedule = await get_schedule(
        db=db,
        code=code,
    )

    presentation = await get_presentation(
        db=db,
        code=schedule.presentation.code,
    )

    if not schedule or not any(
        map(lambda x: user.code == x.user_code, presentation.users)
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to perform this action",
        )

    await db.delete(schedule)
    await db.commit()

    return None
