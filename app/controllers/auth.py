from app.models.users import UserDB, UserLogin, UserUpdate
from app.models.links import UserRoleLink
from app.schemes.users import UserRegistrationScheme
from app.models.auth import Token
from app.internal.utils import SessionDep, auth_controller

from sqlalchemy import select
from fastapi import HTTPException, status
from typing import Union, List


def register_user(session: SessionDep, user: UserRegistrationScheme):
    statement = select(UserDB).where(UserDB.username == user.username)
    is_username_taken = session.exec(statement).scalar()

    if is_username_taken:
        return None

    user_entity = UserDB.parse_obj(user)

    session.add(user_entity)
    session.commit()
    session.refresh(user_entity)

    add_roles_to_user(session=session, user=user_entity, roles=user.roles)

    return user_entity.username


def login_for_access_token(session: SessionDep, user: UserLogin):
    user_entity = check_user(session=session, user=user)

    if not user_entity:
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


def add_roles_to_user(session: SessionDep, user: UserDB, roles: List[int]):
    assigned_roles = [{'user_id': user.id, 'role_id': role} for role in roles]
    session.bulk_insert_mappings(UserRoleLink, assigned_roles)
    session.commit()
