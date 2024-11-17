from sqlalchemy import select

from app.internal.utils import SessionDep
from app.models.users import UserDB
from app.models.links import RoomUserLink
from app.models.rooms import Room


def get_all_users(session: SessionDep):
    statement = select(UserDB)
    users = session.exec(statement).scalars().all()

    return users


def get_rooms_of_user(session: SessionDep, user_id: int):
    statement = select(RoomUserLink).where(RoomUserLink.user_id == user_id)
    room_ids = (room.room_id for room in session.exec(statement).scalars().all())

    if not room_ids:
        return False

    statement = select(Room).where(Room.id.in_(room_ids))
    rooms = session.exec(statement).scalars().all()

    return rooms
