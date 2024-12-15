from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship

from .links import RoomUserLink


class UserBase(SQLModel):
    username: str = Field(index=True)


class UserLogin(UserBase):
    hashed_password: str = Field()


class User(UserBase):
    username: Optional[str] = Field(default='')
    first_name: Optional[str] = Field(default='', alias='firstName')
    second_name: Optional[str] = Field(default='', alias='lastName')
    patronymic: Optional[str] = Field(default='')
    description: Optional[str] = Field(default='Nothing to say about that person')


class UserUpdate(SQLModel):
    first_name: Optional[str] = Field(default='', alias='firstName')
    second_name: Optional[str] = Field(default='', alias='lastName')
    patronymic: Optional[str] = Field(default='')
    role: Optional[int] = Field(default=[0])
    is_active: bool = Field(title="User's activity status", default=True)
    description: Optional[str] = Field(default='Nothing to say about that person')
    hashed_password: Optional[str] = Field(default='')


class UserDB(User, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True)
    hashed_password: str = Field(title="User's password")
    is_active: bool = Field(title="User's activity status", default=False)
    created_rooms: Optional[List["Room"]] = Relationship(
        back_populates='room_creator'
    )
    messages: List["Message"] = Relationship(
        back_populates='sender'
    )
    user_links: Optional[List["RoomUserLink"]] = Relationship(
        back_populates='user'
    )
