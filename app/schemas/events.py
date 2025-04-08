import uuid
from datetime import datetime
from typing import Annotated, List

from pydantic import BaseModel


class PresentationRequest(BaseModel):
    title: str
    description: str
    presenters: List[uuid.UUID]


class Schedule(BaseModel):
    code: uuid.UUID
    room_code: uuid.UUID
    presentation_code: uuid.UUID
    start_time: datetime
    end_time: datetime


class PresentationResponse(BaseModel):
    code: uuid.UUID
    title: str
    description: str
    users: List["PresentationPresenter"]
    schedule: Schedule | None = None


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
