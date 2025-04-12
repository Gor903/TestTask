from fastapi import FastAPI

from app.crud import create_room, get_rooms
from app.db import AsyncSessionMaker, init_db
from .routes import event_router, user_router

app = FastAPI()

app.include_router(user_router)
app.include_router(event_router)


@app.on_event("startup")
async def startup():
    try:
        await init_db()
    except Exception as e:
        print(f"Error during DB initialization: {e}")

    async with AsyncSessionMaker() as session:
        rooms = await get_rooms(session)

        if not rooms:
            await create_room(
                db=session,
                room={
                    "name": "Large room",
                    "sit_count": 100,
                },
            )

            await create_room(
                db=session,
                room={
                    "name": "Small room",
                    "sit_count": 50,
                },
            )


@app.get("/")
async def root():
    return {"message": "Hello, Async FastAPI!"}
