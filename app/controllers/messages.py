from typing import Dict
from sqlalchemy import select
from app.internal.utils import SessionDep
from app.models.messages import Message


def save_message(session: SessionDep, message: Dict[str, str]):
    message = Message.parse_obj(message)

    if message.id is not None:
        message.id = None

    session.add(message)
    session.commit()
    session.refresh(message)

    return message


def get_room_messages(session: SessionDep, room_id: int):
    statement = select(Message).where(Message.room_id == room_id)
    messages = session.exec(statement).scalars().all()

    return messages
