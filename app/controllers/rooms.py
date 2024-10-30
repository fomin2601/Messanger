from sqlmodel import select
from app.models.utils import SessionDep
from app.models.rooms import Room


def get_room_info(session: SessionDep, room_name: str):
    #room = session.exec(select)
    return '1'


def create_room(session: SessionDep, room: Room):
    session.add(room)
    session.commit()
    session.refresh(room)
    return room
