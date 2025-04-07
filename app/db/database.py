from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import databases
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = (
    "postgresql+asyncpg://"
    + f"{os.getenv('POSTGRES_USER')}:"
    + f"{os.getenv('POSTGRES_PASSWORD')}@"
    + f"{os.getenv('POSTGRES_HOST')}:"
    + f"{os.getenv('POSTGRES_PORT')}/"
    + f"{os.getenv('POSTGRES_DB')}"
)

engine = create_async_engine(DATABASE_URL, echo=False, future=True)

AsyncSessionMaker = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)

database = databases.Database(DATABASE_URL)

Base = declarative_base(metadata=MetaData())


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session():
    async with AsyncSessionMaker() as session:
        yield session
