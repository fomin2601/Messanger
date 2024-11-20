from typing import Dict
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
