from typing import Optional
from fastapi import APIRouter, status, HTTPException
from app.controllers import rooms
from app.models.utils import SessionDep
from app.models.rooms import Room


router = APIRouter(
    prefix='/rooms',
    tags=['rooms']
)


@router.get('/{room_id}', status_code=status.HTTP_200_OK)
async def get_room_info(session: SessionDep, room_id: int):
    room = rooms.get_room_info(session=session, room_id=room_id)
    if not room:
        return HTTPException(status_code=404, detail='Room not found')
    return room


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_room(session: SessionDep, room: Room):
    room = rooms.create_room(session=session, room=room)
    return f'Room {str(room.id)} was created'


@router.get('/', tags=['rooms'])
async def get_user_rooms():
    pass
