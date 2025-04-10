import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel
from sqlalchemy.orm import Mapped


class RelationCode(BaseModel):
    code: uuid.UUID


class PresentationPresenter(BaseModel):
    user_code: uuid.UUID


class PresentationRequest(BaseModel):
    title: str
    description: str
    presenters: List[uuid.UUID]


class PresentationResponse(BaseModel):
    code: uuid.UUID
    title: str
    description: str
    users: List[PresentationPresenter]
    schedule: RelationCode | None = None

    class Config:
        from_attributes = True
        orm_mode = True


class PresentationUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    presenters: List[uuid.UUID]


class RoomRequest(BaseModel):
    name: str
    sit_count: int


class RoomResponse(BaseModel):
    code: uuid.UUID
    name: str
    sit_count: int
    schedules: List[RelationCode]


class SchedulesRequest(BaseModel):
    room_code: uuid.UUID
    presentation_code: uuid.UUID
    start_time: datetime
    end_time: datetime


class SchedulesResponse(BaseModel):
    code: uuid.UUID
    room_code: uuid.UUID
    presentation: RelationCode
    start_time: datetime
    end_time: datetime


class ScheduleUpdate(BaseModel):
    room_code: Optional[uuid.UUID] = None
    presentation_code: Optional[uuid.UUID] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
