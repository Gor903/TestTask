import uuid
from typing import List

from pydantic import BaseModel

from app.db.models import Schedule


class PresentationRequest(BaseModel):
    title: str
    description: str
    presenters: List[uuid.UUID]


class PresentationResponse(BaseModel):
    code: uuid.UUID
    title: str
    description: str
    users: List["PresentationPresenter"]


class PresentationPresenter(BaseModel):
    user_code: uuid.UUID


class RoomRequest(BaseModel):
    name: str
    sit_count: int


class RoomResponse(BaseModel):
    code: uuid.UUID
    name: str
    sit_count: int
    schedules: List["RoomSchedules"]


class RoomSchedules(BaseModel):
    schedules: List[uuid.UUID]
