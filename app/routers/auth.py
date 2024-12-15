from fastapi import APIRouter, status, HTTPException, Response
from fastapi.encoders import jsonable_encoder
from app.controllers import auth
from app.models.auth import Token
from app.models.users import UserLogin, UserUpdate
from app.schemes.users import UserRegistrationScheme
from app.internal.utils import SessionDep

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)


@router.post('/login', status_code=status.HTTP_200_OK)
async def login_for_access_token(session: SessionDep, user: UserLogin) -> Token:
    token = auth.login_for_access_token(session=session, user=user)

    return token


@router.post('/registration', status_code=status.HTTP_201_CREATED)
async def registration(response: Response, session: SessionDep, user: UserRegistrationScheme):
    username = auth.register_user(session=session, user=user)

    if not username:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return HTTPException(
            status_code=400,
            detail='That username is taken'
        )

    return jsonable_encoder({'Status': True})


@router.patch('/registration', status_code=status.HTTP_202_ACCEPTED)
async def change_password(session: SessionDep, user: UserLogin, data: UserUpdate):
    username = auth.update_password(session=session, user=user, data=data)

    if username:
        return jsonable_encoder({'Status': True})

    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail='Something really bad happened'
    )

