import pytest
import os
from sqlmodel import create_engine, Session
from sqlalchemy.engine import Engine
from sqlmodel import SQLModel
from typing import Dict, List, Union

from app.internal.utils import create_db_and_tables
from app.models.users import UserDB
from app.models.links import UserRoleLink


@pytest.fixture(scope='session')
def db_url() -> str:
    db_password = os.environ.get('MESSENGER_DB_PASSWORD')
    db_url = f"postgresql://postgres:{db_password}@localhost:5432/test_database_messanger"

    return db_url


@pytest.fixture(scope='session')
def db_engine(db_url: str) -> Engine:
    """Yields a SQLAlchemy engine which will be suppressed after the test session"""

    engine_ = create_engine(db_url, echo=True)

    yield engine_

    engine_.dispose()


@pytest.fixture(scope='class')
def db_tables(db_engine: Engine):
    """Initialize database's tables"""
    create_db_and_tables(db_engine)

    yield

    SQLModel.metadata.drop_all(bind=db_engine)


@pytest.fixture(scope='class')
def db_session(db_engine: Engine) -> Session:
    # connection = db_engine.connect()
    # transaction = connection.begin()
    # session = Session(bind=connection)
    #
    # yield session
    #
    # session.close()
    # transaction.rollback()
    # connection.close()
    with Session(db_engine) as db_session:
        yield db_session


@pytest.fixture(scope='function')
def active_user_parameters() -> Dict[str, Union[int, str, bool]]:
    return {
        'id': 1,
        'username': 'test_username',
        'hashed_password': 'test_hashed_password',
        'is_active': True,
        'first_name': 'test_name',
        'second_name': 'test_second_name',
        'patronymic': 'test_patronymic',
        'description': 'test_description'
    }


@pytest.fixture(scope='function')
def all_roles_for_active_user(active_user_parameters: Dict[str, Union[int, str, bool]]) -> List[Dict[str, int]]:
    return [
        {'user_id': 1, 'role_id': 0},
        {'user_id': 1, 'role_id': 1},
        {'user_id': 1, 'role_id': 2},
        {'user_id': 1, 'role_id': 3}
    ]


@pytest.fixture(scope='module')
def active_user_in_db(
        db_session: Session,
        user_parameters: Dict[str, Union[int, str, bool]],
        roles_for_user: List[Dict[str, int]]
):
    user_entity = UserDB.parse_obj(user_parameters)
    db_session.add(user_entity)
    db_session.commit()

    db_session.bulk_insert_mappings(UserRoleLink, roles_for_user)
    db_session.commit()
