from fastapi import APIRouter, status, HTTPException, Response
from app.controllers import auth
from app.models.auth import Token
from app.models.users import UserDB, UserLogin
from app.internal.utils import auth_controller
from app.internal.utils import SessionDep
from fastapi.security import (
    OAuth2PasswordRequestForm,
)

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)


@router.post('/login', status_code=status.HTTP_200_OK)
async def login_for_access_token(response: Response, session: SessionDep, user: UserLogin) -> Token:
    token = auth.login_for_access_token(session=session, user=user)
    return token


@router.post('/registration', status_code=status.HTTP_201_CREATED)
async def registration(response: Response, session: SessionDep, user: UserDB):
    username = auth.register_user(session=session, user=user)

    if not username:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return HTTPException(status_code=400, detail='That username is taken')

    return username
