import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from app.db.models import (
    Presentation,
    PresentationPresenter,
    Room,
)


async def get_presentation(
    code: uuid.UUID,
    db: AsyncSession,
):
    stmt = (
        select(Presentation)
        .options(selectinload(Presentation.users))
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
        await db.commit()
        await db.refresh(db_presentation)
        await create_presentation_presenter(
            db=db,
            presenters=presenters,
            presentation=db_presentation,
        )
        return db_presentation
    except IntegrityError:
        return False


# TODO: check users' role
async def create_presentation_presenter(
    db: AsyncSession,
    presenters: list,
    presentation: Presentation,
):
    try:
        [
            db.add(
                PresentationPresenter(
                    presentation_code=presentation.code,
                    user_code=code,
                )
            )
            for code in presenters
        ]
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
