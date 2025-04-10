import uuid
from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from starlette import status

from app.crud import get_user_by_code
from app.db.models import (
    Presentation,
    PresentationPresenter,
    Room,
    Schedule,
)


async def get_presentation(
    code: uuid.UUID,
    db: AsyncSession,
):
    stmt = (
        select(Presentation)
        .options(
            selectinload(Presentation.schedule),
            selectinload(Presentation.users),
        )
        .where(Presentation.code == code)
    )

    result = await db.execute(stmt)

    presentation = result.scalar_one_or_none()

    return presentation


async def create_presentation(
    db: AsyncSession,
    presentation: dict,
):
    try:
        presenters = presentation.get("presenters", [])
        db_presentation = Presentation(
            title=presentation.get("title"),
            description=presentation.get("description"),
        )
        db.add(db_presentation)
        # await db.commit()
        # await db.refresh(db_presentation)
        await create_presentation_presenter(
            db=db,
            presenters=presenters,
            presentation=db_presentation,
        )
    except IntegrityError:
        return False

    return db_presentation


async def create_presentation_presenter(
    db: AsyncSession,
    presenters: list,
    presentation: Presentation,
):
    try:
        for code in presenters:
            user = await get_user_by_code(db, code)
            if not user or user.role.value != "presenter":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Wrong role",
                )
            db.add(
                PresentationPresenter(
                    presentation_code=presentation.code,
                    user_code=code,
                )
            )
        await db.commit()
    except IntegrityError:
        ...


async def create_room(
    db: AsyncSession,
    room: dict,
):
    try:
        room = Room(
            name=room.get("name"),
            sit_count=room.get("sit_count"),
        )
        db.add(room)
        await db.commit()
        return room
    except IntegrityError:
        return False


async def create_schedule(
    db: AsyncSession,
    schedule: dict,
):
    try:
        start = schedule.get("start_time")
        end = schedule.get("end_time")
        if end <= start:
            raise Exception("Wrong datetime")

        stmt = (
            select(Schedule)
            .where(Schedule.start_time < end)
            .where(Schedule.end_time > start)
        )
        await db.execute(stmt)
        results = await db.execute(stmt)
        result = results.scalars().all()

        if result:
            raise Exception("Choose  another time")

        schedule = Schedule(
            start_time=start,
            end_time=end,
            room_code=schedule.get("room_code"),
            presentation_code=schedule.get("presentation_code"),
        )

        db.add(schedule)
        await db.commit()

        return schedule

    except IntegrityError:
        ...
    except Exception as e:
        print(e)

    await db.commit()


async def get_schedules(
    db: AsyncSession,
    room_code: uuid.UUID = None,
    future: bool = False,
):

    stmt = select(Schedule).options(
        selectinload(Schedule.presentation),
    )

    if room_code:
        stmt = stmt.where(Schedule.room_code == room_code)
    if future:
        stmt = stmt.where(Schedule.start_time > datetime.now())

    result = await db.execute(stmt)

    schedules = result.scalars().all()

    return schedules


async def get_schedule(
    db: AsyncSession,
    code: uuid.UUID,
):
    stmt = (
        select(Schedule)
        .options(
            selectinload(Schedule.presentation),
        )
        .where(Schedule.code == code)
    )

    result = await db.execute(stmt)

    schedule = result.scalar_one_or_none()

    return schedule


async def get_presentations(
    db: AsyncSession,
    user_code: uuid.UUID,
):
    stmt = (
        select(Presentation)
        .join(
            PresentationPresenter,
            Presentation.code == PresentationPresenter.presentation_code,
        )
        .options(
            selectinload(Presentation.users),
            selectinload(Presentation.schedule),
        )
        .where(PresentationPresenter.user_code == user_code)
    )

    res = await db.execute(stmt)

    presentations = res.scalars().all()

    return presentations


async def get_rooms(
    db: AsyncSession,
):
    stmt = select(Room).options(selectinload(Room.schedules))

    res = await db.execute(stmt)

    rooms = res.scalars().all()

    return rooms


async def get_room(
    db: AsyncSession,
    code: uuid.UUID,
):
    stmt = select(Room).options(selectinload(Room.schedules)).where(Room.code == code)

    res = await db.execute(stmt)

    room = res.scalar_one_or_none()

    return room
