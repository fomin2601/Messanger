import pytest
from sqlmodel import Session
from sqlalchemy import select
from app.models.users import UserDB
from app.models.links import UserRoleLink
from app.schemes.users import UserRegistrationScheme
from app.controllers.auth import register_user


@pytest.mark.usefixtures('db_session')
class TestAuthController:
    def test_register_user__user_and_his_roles_was_added_to_database(
            self,
            db_session: Session,
            user_entity: UserRegistrationScheme
    ):
        status = register_user(session=db_session, user=user_entity)

        assert status == user_entity.username

        statement = select(UserDB).where(UserDB.username == user_entity.username)
        created_user = db_session.exec(statement).scalar()

        assert created_user.username == user_entity.username
        assert created_user.hashed_password == user_entity.hashed_password
        assert created_user.first_name == user_entity.first_name
        assert created_user.second_name == user_entity.second_name
        assert created_user.patronymic == user_entity.patronymic
        assert created_user.description == user_entity.description

        statement = select(UserRoleLink).where(UserRoleLink.user_id == created_user.id)
        created_role_links = db_session.exec(statement).scalars().all()

        for user_entity_role_id, created_role_link in zip(user_entity.roles, created_role_links):
            assert user_entity_role_id == created_role_link.role_id

    def test_register_user__attempt_to_save_user_with_duplicated_username_returned_none(
            self,
            db_session: Session,
            user_entity: UserRegistrationScheme
    ):
        user_entity_with_duplicated_username = user_entity.model_copy()
        user_entity_with_duplicated_username.username = 'default_username'

        status = register_user(session=db_session, user=user_entity_with_duplicated_username)

        assert status is None

    def test_register_user__attempt_to_save_user_without_accorded_roles_returned_none(
            self,
            db_session: Session,
            user_entity: UserRegistrationScheme
    ):
        user_entity_without_roles = user_entity.model_copy()
        user_entity_without_roles.roles = []

        status = register_user(session=db_session, user=user_entity_without_roles)

        assert status is None

    def test_login_for_access_token__user_with_valid_credentials_got_token(
            self,
            db_session: Session,
            credentials: str
    ):
        pass
