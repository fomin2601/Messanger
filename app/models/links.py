from sqlmodel import SQLModel, Field, Relationship
from typing import Optional


class RoomUserLink(SQLModel, table=True):
    room_id: int = Field(foreign_key='room.id', primary_key=True)
    user_id: int = Field(foreign_key='userdb.id', primary_key=True)


class RoomUserLinkScheme(SQLModel):
    room_id: int
    user_id: int


class UserRoleLink(SQLModel, table=True):
    user_id: int = Field(foreign_key='userdb.id', primary_key=True)
    role_id: int = Field(foreign_key='userrole.id', primary_key=True)
    user: Optional["UserDB"] = Relationship(back_populates='roles')
    role: Optional['UserRole'] = Relationship(back_populates='user_link')
