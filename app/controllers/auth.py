from app.models.users import UserDB, UserLogin, UserUpdate
from app.models.auth import Token
from app.internal.utils import SessionDep, auth_controller

from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from fastapi import HTTPException, status
from typing import Union


def register_user(session: SessionDep, user: UserDB):
    statement = select(UserDB).where(UserDB.username == user.username)
    is_username_taken = session.exec(statement).scalar()

    if is_username_taken:
        return None

    try:
        session.add(user)
        session.commit()
        session.refresh(user)

    except IntegrityError:
        user.id = None
        session.rollback()
        session.add(user)
        session.commit()
        session.refresh(user)

    return user.username


def login_for_access_token(session: SessionDep, user: UserLogin):
    user_entity = check_user(session=session, user=user)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    access_token = auth_controller.create_jwt(
        data={'sub': user_entity.username},
    )
    return Token(access_token=access_token, token_type='Bearer')


def check_user(session: SessionDep, user: Union[UserDB, UserLogin, UserUpdate]):
    statement = select(UserDB).where(UserDB.username == user.username)
    user_entity = session.exec(statement).scalar()

    if user_entity is None:
        return False

    if user_entity.hashed_password != user.hashed_password:
        return False

    return user_entity


def update_password(session: SessionDep, user: UserLogin, data: UserUpdate):
    user_entity = check_user(session=session, user=user)

    if not user_entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User doesn\'t exist'
        )

    data_for_update = data.model_dump(exclude_unset=True)
    user_entity.sqlmodel_update(data_for_update)
    session.add(user_entity)
    session.commit()
    session.refresh(user_entity)

    return True

