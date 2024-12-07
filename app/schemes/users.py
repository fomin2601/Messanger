from pydantic import BaseModel
from typing import Optional, List

from app.models.roles import UserRole
from app.models.rooms import Room
from .messages import MessageScheme


class UserRegistrationScheme(BaseModel):
    username: str
    hashed_password: str
    first_name: str
    second_name: str
    patronymic: Optional[str]
    roles: List[int]
    description: Optional[str]


class UserPublicScheme(BaseModel):
    id: int
    username: str
    first_name: str
    second_name: str
    patronymic: Optional[str]
    roles: Optional[List[UserRole]]
    description: Optional[str]


class UserRoomScheme(BaseModel):
    room: Room
    members: Optional[List[UserPublicScheme]]
    last_message: Optional[MessageScheme]
