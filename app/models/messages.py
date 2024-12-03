from sqlmodel import SQLModel, Field, Relationship
import datetime
from typing import Optional


def get_datetime_factory():
    return datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")


class Message(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    text: str = Field(nullable=False)
    date_time: str = Field(default_factory=get_datetime_factory, nullable=False)
    status: str = Field(default='Common message', nullable=False)
    message_type: str = Field(default='text')
    sender_id: int = Field(foreign_key='userdb.id')
    sender: Optional["UserDB"] = Relationship(back_populates='messages')
    room_id: int = Field(foreign_key='room.id')
    room: Optional["Room"] = Relationship(back_populates='messages')



