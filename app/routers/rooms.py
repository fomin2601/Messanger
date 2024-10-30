from fastapi import APIRouter
from app.controllers import rooms
from app.models.utils import SessionDep
from app.models.rooms import Room


router = APIRouter(
    prefix='/rooms',
    tags=['rooms']
)


@router.get('/{room_name}')
async def get_room_info(session: SessionDep, room_name: str):
    return rooms.get_room_info(session=session, room_name=room_name)


@router.put('/{room_name}')
async def create_room(session: SessionDep, room: Room):
    status = rooms.create_room(session=session, room=room)
    return 'Done'


@router.get('/', tags=['rooms'])
async def get_user_rooms():
    pass
