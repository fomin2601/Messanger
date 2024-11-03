from sqlmodel import select
from sqlalchemy.exc import IntegrityError
from app.models.utils import SessionDep
from app.models.rooms import Room


def get_room_info(session: SessionDep, room_id: int):
    room = session.get(Room, room_id)
    return room


def create_room(session: SessionDep, room: Room):
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

    return room
