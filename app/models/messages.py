from sqlmodel import SQLModel, Field, Relationship
import datetime
from typing import Optional
from .users import UserDB


class Message(SQLModel):
    id: Optional[int] = Field(default=None, primary_key=True)
    text: str = Field(nullable=False)
    date_time: datetime.datetime = Field(default_factory=datetime.datetime.utcnow, nullable=False)
    status: str = Field(default='Common message', nullable=False)
    sender_id: int = Field(foreign_key='userdb.id')
    sender: UserDB = Relationship(back_populates='messages')
