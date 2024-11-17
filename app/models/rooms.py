from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from .users import UserDB
from .links import RoomUserLink, RoomUserLinkPublic
from pydantic import BaseModel


class Room(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    room_name: str = Field(index=True, alias='name')
    users: Optional[list["UserDB"]] = Relationship(
        back_populates='rooms',
        link_model=RoomUserLink
    )
    is_group: bool = Field(default=False, alias='isGroup')

    def __repr__(self):
        return self.room_name


class RoomWithUsersScheme(BaseModel):
    id: int
    room_name: str
    is_group: bool
    users: Optional[List[RoomUserLinkPublic]]
