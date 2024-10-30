from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from .rooms import RoomUserLink, Room


class User(SQLModel):
    id: int
    username: str = Field(index=True)
    name: Optional[str] = Field(default='Jonh')
    second_name: Optional[str] = Field(default='Doe')

class UserDB(User, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str = Field()
    rooms: list[Room] = Relationship(
        back_populates='users',
        link_model=RoomUserLink
    )
