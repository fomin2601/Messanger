from typing import List, Optional
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from app.internal.utils import SessionDep
from app.models.rooms import Room
from app.models.links import RoomUserLink, UserRoleLink
from app.models.users import UserDB
from app.schemes.users import UserPublicScheme


def get_room_info(session: SessionDep, room_id: int):
    room = session.get(Room, room_id)
    return room


def create_room(session: SessionDep, room: Room, users: Optional[List[int]] = None):
    try:
        session.add(room)
        session.commit()
        session.refresh(room)

    except IntegrityError:
        room.id = None
        session.rollback()
        session.add(room)
        session.commit()
        session.refresh(room)

    if users:
        add_users_to_room(session=session, room_id=room.id, users=users)

    return room


def add_users_to_room(session: SessionDep, room_id: int, users: List[int]):
    if not users:
        return False

    room_entity = session.get(Room, room_id)
    users_entities = [session.get(UserDB, user_id) for user_id in users]

    data = [{'room_id': room_entity.id, 'user_id': user.id} for user in users_entities if user is not None]
    session.bulk_insert_mappings(RoomUserLink, data)
    session.commit()
    return True


def get_users_in_room(session: SessionDep, room_id: int):
    statement = select(RoomUserLink).where(RoomUserLink.room_id == room_id)
    users_id = [user.user_id for user in session.exec(statement).scalars().all()]

    if not users_id:
        return False

    statement = select(UserDB).where(UserDB.id.in_(users_id))
    users = session.exec(statement).scalars().all()
    users_json = []
    for user in users:
        user_json = user.model_dump()
        statement = select(UserRoleLink).where(UserRoleLink.user_id == user_json['id'])
        roles = [user_role_link.role for user_role_link in session.exec(statement).scalars().all()]
        user_json.update({'roles': roles})
        users_json.append(UserPublicScheme.parse_obj(user_json))

    return users_json
