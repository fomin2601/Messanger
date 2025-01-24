import pytest
import time
from fastapi import HTTPException
from sqlmodel import Session
from sqlalchemy import select
from app.models.users import UserDB, UserUpdate
from app.models.links import UserRoleLink
from app.schemes.users import UserRegistrationScheme, UserLoginScheme
from app.controllers.auth import (
    register_user,
    login_for_access_token,
    check_user,
    update_password,
    add_roles_to_user
)
from app.internal.utils import auth_controller
from app.models.auth import Token


@pytest.mark.usefixtures('db_session')
class TestAuthController:
    def test_register_user__user_and_his_roles_was_added_to_database(
            self,
            db_session: Session,
            user_registration_entity: UserRegistrationScheme
    ):
        status = register_user(session=db_session, user=user_registration_entity)

        assert status == user_registration_entity.username

        statement = select(UserDB).where(UserDB.username == user_registration_entity.username)
        created_user = db_session.exec(statement).scalar()

        assert created_user.username == user_registration_entity.username
        assert created_user.hashed_password == user_registration_entity.hashed_password
        assert created_user.first_name == user_registration_entity.first_name
        assert created_user.second_name == user_registration_entity.second_name
        assert created_user.patronymic == user_registration_entity.patronymic
        assert created_user.description == user_registration_entity.description

        statement = select(UserRoleLink).where(UserRoleLink.user_id == created_user.id)
        created_role_links = db_session.exec(statement).scalars().all()

        for user_entity_role_id, created_role_link in zip(user_registration_entity.roles, created_role_links):
            assert user_entity_role_id == created_role_link.role_id

    def test_register_user__attempt_to_save_user_with_duplicated_username_returned_none(
            self,
            db_session: Session,
            user_registration_entity: UserRegistrationScheme
    ):
        user_entity_with_duplicated_username = user_registration_entity.model_copy()
        user_entity_with_duplicated_username.username = 'default_active_username'

        status = register_user(session=db_session, user=user_entity_with_duplicated_username)

        assert status is None

    def test_register_user__attempt_to_save_user_without_accorded_roles_returned_none(
            self,
            db_session: Session,
            user_registration_entity: UserRegistrationScheme
    ):
        user_entity_without_roles = user_registration_entity.model_copy()
        user_entity_without_roles.roles = []

        status = register_user(session=db_session, user=user_entity_without_roles)

        assert status is None

    def test_login_for_access_token__user_with_valid_credentials_got_token(
            self,
            db_session: Session,
            credentials_active: UserLoginScheme
    ):
        jwt_token = login_for_access_token(session=db_session, user=credentials_active)
        decoded_token = auth_controller.decode_jwt(token=jwt_token.access_token)

        assert type(jwt_token) is Token
        assert decoded_token['sub'] == credentials_active.username
        assert decoded_token['exp'] > time.time()
        assert decoded_token['status'] is True

    def test_login_for_access_token__missing_user_didnt_get_token(
            self,
            db_session: Session,
            missing_user: UserLoginScheme
    ):
        with pytest.raises(HTTPException) as exc:
            jwt_token = login_for_access_token(session=db_session, user=missing_user)

        assert exc.value.status_code == 401
        assert exc.value.detail == 'Incorrect username or password'

    def test_login_for_access_token__inactive_user_didnt_get_token(
            self,
            db_session: Session,
            credentials_inactive: UserLoginScheme
    ):
        with pytest.raises(HTTPException) as exc:
            jwt_token = login_for_access_token(session=db_session, user=credentials_inactive)

        assert exc.value.status_code == 401
        assert exc.value.detail == 'User is inactive'

    def test_check_user__user_entity_returned_for_existing_user(
            self,
            db_session: Session,
            credentials_active: UserLoginScheme
    ):
        user_entity = check_user(session=db_session, user=credentials_active)

        assert user_entity.username == 'default_active_username'
        assert user_entity.hashed_password == 'default_hashed_password'
        assert user_entity.first_name == 'default_name'
        assert user_entity.second_name == 'default_second_name'
        assert user_entity.patronymic == 'default_patronymic'
        assert user_entity.description == 'default_description'
        assert user_entity.is_active is True

    def test_check_user__missing_user_returned_false(
            self,
            db_session: Session,
            missing_user: UserLoginScheme
    ):
        user_entity = check_user(session=db_session, user=missing_user)

        assert user_entity is False

    def test_check_user__user_with_wrong_password_returned_false(
            self,
            db_session: Session,
            credentials_active: UserLoginScheme
    ):
        user_with_wrong_password = credentials_active.model_copy()
        user_with_wrong_password.hashed_password = 'wrong_password'

        user_entity = check_user(session=db_session, user=user_with_wrong_password)

        assert user_entity is False

    def test_update_password__user_password_updated(
            self,
            db_session: Session,
            credentials_for_update: UserLoginScheme,
            user_password_for_update: UserUpdate
    ):
        status = update_password(session=db_session, user=credentials_for_update, data=user_password_for_update)

        assert status is True

        updated_credentials = credentials_for_update
        updated_credentials.hashed_password = user_password_for_update.hashed_password

        user_entity = check_user(session=db_session, user=updated_credentials)

        assert user_entity.hashed_password == user_password_for_update.hashed_password

    def test_update_password__missing_user_raised_error(
            self,
            db_session: Session,
            missing_user: UserLoginScheme,
            user_password_for_update: UserUpdate
    ):
        with pytest.raises(HTTPException):
            status = update_password(session=db_session, user=missing_user, data=user_password_for_update)

    def test_add_roles_to_user__roles_added_to_user(
            self,
            db_session: Session,
            credentials_inactive: UserLoginScheme
    ):
        user_entity = check_user(session=db_session, user=credentials_inactive)
        roles = [1, 2, 3]

        add_roles_to_user(session=db_session, user=user_entity, roles=roles)

        statement = select(UserRoleLink).where(UserRoleLink.user_id == user_entity.id)
        user_roles = sorted(db_session.exec(statement).scalars().all(), key= lambda x: x.role_id)

        for role, user_role in zip(roles, user_roles):
            assert role == user_role.role_id