import pytest
from sqlmodel import Session
from app.models.users import UserDB
from app.controllers.auth import check_user


@pytest.mark.usefixtures('db_tables')
class TestAuthController:
    def test_check_existing_user__exiting_user_gotten_from_database(self, db_session: Session):
        user_entity = db_session.get(UserDB, 1)
        assert user_entity is not None
        assert user_entity.id == 1