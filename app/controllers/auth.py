from app.models.users import UserDB, UserLogin
from app.models.auth import Token, TokenData
from app.internal.utils import SessionDep, auth_controller

from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from datetime import timedelta, datetime, timezone
import jwt
from jwt.exceptions import InvalidTokenError
from fastapi import HTTPException, status


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
    user_entity = check_user(session, user)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    access_token = auth_controller.create_jwt(
        data={'sub': user_entity.username},
    )
    return Token(access_token=access_token, token_type='Bearer')


def check_user(session: SessionDep, user: UserLogin):
    statement = select(UserDB).where(UserDB.username == user.username)
    user_entity = session.exec(statement).scalar()
    if user_entity is None:
        return False

    if user_entity.hashed_password != user.hashed_password:
        return False

    return user_entity




