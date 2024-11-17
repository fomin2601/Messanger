from sqlmodel import SQLModel, Field


class RoomUserLink(SQLModel, table=True):
    room_id: int = Field(foreign_key='room.id', primary_key=True)
    user_id: int = Field(foreign_key='userdb.id', primary_key=True)


class RoomUserLinkPublic(SQLModel):
    room_id: int
    user_id: int
