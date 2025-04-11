import uuid
from typing import List
from pydantic import BaseModel, ConfigDict, EmailStr, SecretStr


class UserRequest(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: SecretStr
    role: str

    model_config = ConfigDict(from_attributes = True)

class UserResponse(BaseModel):
    code: uuid.UUID
    first_name: str
    last_name: str
    email: EmailStr
    role: str
    presentations: List["UserPresentationPresenter"]

    model_config = ConfigDict(from_attributes = True)


class UserPresentationPresenter(BaseModel):
    presentation_code: uuid.UUID


class UserUpdate(BaseModel):
    first_name: str = None
    last_name: str = None
    email: EmailStr = None
    password: SecretStr = None
    refresh_token: str = None


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class RefreshRequest(BaseModel):
    refresh_token: str
