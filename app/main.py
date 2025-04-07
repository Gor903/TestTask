from fastapi import FastAPI
from app.db.database import init_db

app = FastAPI()


@app.on_event("startup")
async def startup():
    try:
        await init_db()
    except Exception as e:
        print(f"Error during DB initialization: {e}")


@app.get("/")
async def root():
    return {"message": "Hello, Async FastAPI!"}
