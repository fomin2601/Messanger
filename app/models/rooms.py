from typing import Optional
from sqlmodel import SQLModel, Field, Relationship


class RoomUserLink(SQLModel, table=True):
    room_id: int = Field(foreign_key='room.id', primary_key=True)
    user_id: int = Field(foreign_key='userdb.id', primary_key=True)


class Room(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    room_name: str = Field(index=True)
    users: list["User"] = Relationship(
        back_populates='rooms',
        link_model=RoomUserLink
    )
