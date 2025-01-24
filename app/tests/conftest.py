import pytest
from sqlmodel import create_engine, Session, insert
from sqlalchemy.engine import Engine
from sqlmodel import SQLModel
from sqlmodel.pool import StaticPool
from app.schemes.users import UserRegistrationScheme, UserLoginScheme, UserUpdateScheme
from app.models.users import UserUpdate

predefined_tables = {
    'userrole': [
        {'id': 0, 'role_name': 'Администратор'},
        {'id': 1, 'role_name': 'Руководитель'},
        {'id': 2, 'role_name': 'Методист'},
        {'id': 3, 'role_name': 'Владелец'},
    ],
    'userdb': [
        {
            'id': 0,
            'username': 'default_active_username',
            'hashed_password': 'default_hashed_password',
            'is_active': True,
            'first_name': 'default_name',
            'second_name': 'default_second_name',
            'patronymic': 'default_patronymic',
            'description': 'default_description',
        },
        {
            'id': 1,
            'username': 'default_inactive_username',
            'hashed_password': 'default_hashed_password',
            'is_active': False,
            'first_name': 'default_name',
            'second_name': 'default_second_name',
            'patronymic': 'default_patronymic',
            'description': 'default_description',
        },
        {
            'id': 2,
            'username': 'default_user_for_password_update',
            'hashed_password': 'default_hashed_password',
            'is_active': False,
            'first_name': 'default_name',
            'second_name': 'default_second_name',
            'patronymic': 'default_patronymic',
            'description': 'default_description',
        },
    ],
    'userrolelink': [
        {'user_id': 0, 'role_id': 0},
    ]
}


def insert_default_db_data(engine: Engine):
    with engine.connect() as connection:
        for table in predefined_tables:
            connection.execute(
                insert(SQLModel.metadata.tables[table]),
                predefined_tables[table]
            )
            connection.commit()


@pytest.fixture(scope='class')
def db_session() -> Session:
    db_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(db_engine)
    insert_default_db_data(db_engine)

    with Session(db_engine) as db_session:
        yield db_session


@pytest.fixture(scope='function')
def user_registration_entity() -> UserRegistrationScheme:
    return UserRegistrationScheme(
        username='test_username',
        hashed_password='test_hashed_password',
        first_name='test_name',
        second_name='test_surname',
        patronymic='test_patronymic',
        roles=[0, 1, 2, 3],
        description='test_description'
    )


@pytest.fixture(scope='function')
def credentials_active() -> UserLoginScheme:
    return UserLoginScheme(
        username='default_active_username',
        hashed_password='default_hashed_password'
    )


@pytest.fixture(scope='function')
def credentials_inactive() -> UserLoginScheme:
    return UserLoginScheme(
        username='default_inactive_username',
        hashed_password='default_hashed_password'
    )


@pytest.fixture(scope='function')
def credentials_for_update() -> UserLoginScheme:
    return UserLoginScheme(
        username='default_user_for_password_update',
        hashed_password='default_hashed_password'
    )


@pytest.fixture(scope='function')
def missing_user() -> UserLoginScheme:
    return UserLoginScheme(
        username='missing_username',
        hashed_password='default_hashed_password'
    )


@pytest.fixture(scope='function')
def user_password_for_update() -> UserUpdate:
    return UserUpdate(
        hashed_password='updated_password',
    )


@pytest.fixture(scope='function')
def token_expiration_time() -> int:
    return 24 * 60 * 7 * 60
