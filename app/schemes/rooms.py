from pydantic import BaseModel
from typing import Optional, List
from .users import UserPublicScheme


class RoomWithUsersScheme(BaseModel):
    id: int
    room_name: str
    is_group: bool
    creator_id: int
    users: Optional[List[UserPublicScheme]]
