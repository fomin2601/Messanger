from sqlalchemy import select, delete

from app.internal.utils import SessionDep, auth_controller
from app.models.users import UserDB
from app.models.links import RoomUserLink, UserRoleLink
from app.models.messages import Message
from app.controllers.rooms import get_users_in_room
from app.schemes.rooms import UserRoomScheme
from app.schemes.messages import MessageScheme
from app.schemes.users import UserPublicScheme, UserUpdateScheme


def get_all_users(session: SessionDep):
    statement = select(UserDB)
    users = session.exec(statement).scalars().all()

    data = []
    for user in users:
        user_json = user.model_dump()
        statement = select(UserRoleLink).where(UserRoleLink.user_id == user.id)
        roles = session.exec(statement).scalars().all()
        user_json.update({'roles': [role.role for role in roles]})
        data.append(user_json)

    return data


def get_rooms_of_user(session: SessionDep, user_id: int):
    statement = select(RoomUserLink).where(RoomUserLink.user_id == user_id)
    room_user_links = session.exec(statement).scalars().all()

    if not room_user_links:
        return False

    rooms = []
    for link in room_user_links:
        room = link.room

        if room.is_group:
            members = []

        else:
            members = get_users_in_room(
                session=session,
                room_id=room.id
            )

        statement = select(Message).where(Message.room_id == room.id).order_by(Message.id.desc())
        last_message = session.exec(statement).scalars().first()

        if last_message is not None:
            sender = last_message.sender
            statement = select(UserRoleLink).where(UserRoleLink.user_id == sender.id)
            roles = [role.role for role in session.exec(statement).scalars().all()]
            sender = sender.model_dump()
            sender.update({'roles': roles})
            sender = UserPublicScheme.parse_obj(sender)

            last_message = MessageScheme.parse_obj({
                'message': last_message,
                'sender': sender
            })

        data = {'room': room, 'members': members, 'last_message': last_message}

        rooms.append(UserRoomScheme.parse_obj(data))

    #TODO: Make mesage sorting by date
    rooms.sort(key=lambda elem: elem.last_message.message.id if elem.last_message is not None else float('inf'))

    return rooms


def get_current_user(session: SessionDep, token: str):
    username = auth_controller.decode_jwt(token)['sub']
    statement = select(UserDB).where(UserDB.username == username)
    user = session.exec(statement).scalar()

    user_json = user.model_dump()
    statement = select(UserRoleLink).where(UserRoleLink.user_id == user.id)
    roles = session.exec(statement).scalars().all()
    user_json.update({'roles': [role.role for role in roles]})

    return user_json


def delete_user(session: SessionDep, user_id: int):
    statement = delete(UserRoleLink).where(UserRoleLink.user_id == user_id)
    session.exec(statement)

    statement = delete(RoomUserLink).where(RoomUserLink.user_id == user_id)
    session.exec(statement)

    statement = delete(UserDB).where(UserDB.id == user_id)
    session.exec(statement)

    session.commit()
