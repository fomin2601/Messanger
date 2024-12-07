from pydantic import BaseModel
from typing import Optional, List
from .users import UserPublicScheme
from app.models.rooms import Room
from .messages import MessageScheme


class RoomWithUsersScheme(BaseModel):
    id: int
    room_name: str
    is_group: bool
    creator_id: int
    users: Optional[List[UserPublicScheme]]


class UserRoomScheme(BaseModel):
    room: Room
    members: Optional[List[UserPublicScheme]]
    last_message: Optional[MessageScheme]
