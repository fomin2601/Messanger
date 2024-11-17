from fastapi import APIRouter, Depends, status, HTTPException
from typing import List, Annotated

from app.internal.utils import JWTBearer, SessionDep
from app.controllers import users
from app.models.users import User
from app.models.rooms import Room

router = APIRouter(
    prefix='/users',
    tags=['users'],
    dependencies=[Depends(JWTBearer())]
)


@router.get('/userlist', status_code=status.HTTP_200_OK, response_model=List[User])
async def get_all_users(session: SessionDep):
    return users.get_all_users(session)


@router.get('/{user_id}', status_code=status.HTTP_200_OK, response_model=List[Room])
async def get_rooms_of_user(session: SessionDep, user_id: int):
    rooms = users.get_rooms_of_user(session=session, user_id=user_id)

    if not rooms:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User is not included in any room'
        )

    return rooms


@router.get('/', status_code=status.HTTP_200_OK, response_model=User)
async def get_current_user(token: Annotated[str, Depends(JWTBearer())], session: SessionDep):
    user = users.get_current_user(session=session, token=token)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Current user is not in our system, where is he from?'
        )

    return user
