import uuid
from typing import List

from pydantic import BaseModel


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
