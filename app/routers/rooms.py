from fastapi import APIRouter, status, HTTPException, Depends
from fastapi.encoders import jsonable_encoder
from typing import List, Optional
from app.controllers import rooms
from app.internal.utils import SessionDep, JWTBearer
from app.models.rooms import Room, RoomWithUsersScheme


router = APIRouter(
    prefix='/rooms',
    tags=['rooms'],
    dependencies=[Depends(JWTBearer())],
)


@router.get('/{room_id}', status_code=status.HTTP_200_OK, response_model=RoomWithUsersScheme)
async def get_room_info(
        session: SessionDep,
        room_id: int
):
    room = rooms.get_room_info(session=session, room_id=room_id)
    if not room:
        raise HTTPException(status_code=404, detail='Room not found')

    users = rooms.get_users_in_room(session=session, room_id=room_id)

    if not users:
        data = room.model_dump()
        data.update({'users': []})

        return data

    data = room.model_dump()
    data.update({'users': users})

    return data


@router.post('/{room_id}', status_code=status.HTTP_200_OK)
async def add_users_to_room(session: SessionDep, room_id: int, users: List[int]):
    status = rooms.add_users_to_room(session=session, room_id=room_id, users=users)

    if status:
        return jsonable_encoder({'Status': True})

    raise HTTPException(status_code=404, detail='Userlist is empty or room not found')


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_room(session: SessionDep, room: Room, users: Optional[List[int]] = None):
    room = rooms.create_room(session=session, room=room, users=users)
    return room.id
