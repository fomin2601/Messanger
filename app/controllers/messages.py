from typing import Dict
from sqlalchemy import select
from app.internal.utils import SessionDep
from app.models.messages import Message
from app.models.links import UserRoleLink
from app.schemes.messages import MessageScheme
from app.schemes.users import UserPublicScheme


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
    senders = [message.sender.model_dump() for message in messages]
    senders_json = []
    for sender in senders:
        statement = select(UserRoleLink).where(UserRoleLink.user_id == sender['id'])
        roles = [user_role_link.role for user_role_link in session.exec(statement).scalars().all()]
        sender.update({'roles': roles})
        senders_json.append(UserPublicScheme.parse_obj(sender))

    messages = [MessageScheme(message=message, sender=sender) for message, sender in zip(messages, senders_json)]

    return messages
