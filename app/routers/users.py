from fastapi import APIRouter, Depends, status, Response, HTTPException
from fastapi.encoders import jsonable_encoder
from typing import List

from app.internal.utils import JWTBearer, SessionDep
from app.controllers import users
from app.models.users import User

router = APIRouter(
    prefix='/users',
    tags=['users'],
    dependencies=[Depends(JWTBearer())]
)


@router.get('/userlist', status_code=status.HTTP_200_OK, response_model=List[User])
async def get_all_users(session: SessionDep):
    return users.get_all_users(session)
