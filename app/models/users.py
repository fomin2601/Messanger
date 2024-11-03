from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from .links import RoomUserLink


class User(SQLModel):
    id: int
    username: str = Field(index=True)
    first_name: Optional[str] = Field(default='', alias='firstName')
    second_name: Optional[str] = Field(default='', alias='lastName')
    patronymic: Optional[str] = Field(default='')
    role: Optional[int] = Field(default=0)
    description: Optional[str] = Field()


class UserDB(User, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str = Field()
    rooms: list["Room"] = Relationship(
        back_populates='users',
        link_model=RoomUserLink
    )
