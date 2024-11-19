from sqlmodel import SQLModel, Field, Relationship, ForeignKey
import datetime
from typing import Optional


class Message(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    text: str = Field(nullable=False)
    date_time: datetime.datetime = Field(default_factory=datetime.datetime.utcnow, nullable=False)
    status: str = Field(default='Common message', nullable=False)
    message_type: str = Field(default='text')
    sender_id: int = Field(foreign_key='userdb.id')
    sender: Optional["UserDB"] = Relationship(back_populates='messages')
