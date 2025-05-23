import uuid
from typing import List

from fastapi import APIRouter, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import (create_presentation, create_registration, create_schedule,
                      get_presentation, get_presentations, get_room, get_rooms,
                      get_schedule, get_schedules, update_presentation,
                      update_schedule)
from app.crud.events import get_registration
from app.dependencies import (db_dependency, user_dependency)
from app.schemas import (PresentationRequest, PresentationResponse,
                         PresentationUpdate, RegistrationResponse, RoomResponse,
                         ScheduleUpdate, SchedulesRequest, SchedulesResponse)

router = APIRouter(prefix="/events", tags=["Events"])


@router.post(
    path="/presentation/create",
    response_model=PresentationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def presentation_create(
    presentation: PresentationRequest,
    user: user_dependency,
    db: AsyncSession = db_dependency,
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
    path="/schedule/create",
    response_model=SchedulesResponse,
    status_code=status.HTTP_201_CREATED,
)
async def schedule_create(
    schedule: SchedulesRequest,
    user: user_dependency,
    db: AsyncSession = db_dependency,
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


@router.post(
    path="/registration/create",
    response_model=RegistrationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def registration_create(
    user: user_dependency,
    schedule_code: uuid.UUID,
    db: AsyncSession = db_dependency,
):
    if user.role.value != "listener":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect request",
        )

    registration = await create_registration(
        db=db,
        schedule_code=schedule_code,
        user_code=user.code,
    )

    return registration


@router.get(
    path="/presentations",
    response_model=List[PresentationResponse],
    status_code=status.HTTP_200_OK,
)
async def presentations_all(
    user: user_dependency,
    db: AsyncSession = db_dependency,
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
    db: AsyncSession = db_dependency,
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
    db: AsyncSession = db_dependency,
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
    db: AsyncSession = db_dependency,
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
    db: AsyncSession = db_dependency,
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
    db: AsyncSession = db_dependency,
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


@router.patch(
    path="/presentation/update/{presentation_code}",
    response_model=PresentationResponse,
    status_code=status.HTTP_200_OK,
)
async def presentation_put_update(
    user: user_dependency,
    presentation_code: uuid.UUID,
    presentation_update: PresentationUpdate,
    db: AsyncSession = db_dependency,
):
    presentation = await get_presentation(
        db=db,
        code=presentation_code,
    )

    if not presentation or not any(
        map(lambda x: user.code == x.user_code, presentation.users)
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to perform this action",
        )

    presentation_update = presentation_update.model_dump(exclude_none=True)

    presentation = await update_presentation(
        db=db,
        presentation=presentation,
        presentation_update=presentation_update,
    )

    if not presentation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Wrong input",
        )

    await db.refresh(presentation)
    presentation = await get_presentation(
        db=db,
        code=presentation.code,
    )

    return presentation


@router.patch(
    path="/schedule/update/{schedule_code}",
    response_model=SchedulesResponse,
    status_code=status.HTTP_200_OK,
)
async def schedule_put_update(
    user: user_dependency,
    schedule_code: uuid.UUID,
    schedule_update: ScheduleUpdate,
    db: AsyncSession = db_dependency,
):
    schedule = await get_schedule(
        db=db,
        code=schedule_code,
    )

    if not schedule or not any(
        map(
            lambda x: x.presentation_code == schedule.presentation.code,
            user.presentations,
        )
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to perform this action",
        )

    schedule_update = schedule_update.model_dump(exclude_none=True)

    schedule = await update_schedule(
        db=db,
        schedule=schedule,
        schedule_update=schedule_update,
    )

    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Wrong input",
        )

    await db.refresh(schedule)
    schedule = await get_schedule(
        db=db,
        code=schedule.code,
    )

    return schedule


@router.delete(
    path="/presentation/{presentation_code}",
)
async def presentation_delete(
    code: uuid.UUID,
    user: user_dependency,
    db: AsyncSession = db_dependency,
):
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
    db: AsyncSession = db_dependency,
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


@router.delete(
    path="/registration/{registration_code}",
)
async def registration_delete(
    schedule_code: uuid.UUID,
    user: user_dependency,
    db: AsyncSession = db_dependency,
):
    registration = await get_registration(
        schedule_code=schedule_code,
        db=db,
        user_code=user.code,
    )
    if not registration:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registration not found",
        )

    await db.delete(registration)
    await db.commit()
