from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from .users import UserDB
from app.schemes.users import UserPublicScheme
from .links import RoomUserLink
from pydantic import BaseModel


class Room(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    room_name: str = Field(index=True, alias='name')
    is_group: bool = Field(default=False, alias='isGroup')
    creator_id: int = Field(foreign_key='userdb.id')
    room_creator: Optional[list["UserDB"]] = Relationship(
        back_populates='created_rooms',
    )
    messages: List["Message"] = Relationship(
        back_populates='room'
    )

    def __repr__(self):
        return self.room_name


class RoomWithUsersScheme(BaseModel):
    id: int
    room_name: str
    is_group: bool
    creator_id: int
    users: Optional[List[UserPublicScheme]]
