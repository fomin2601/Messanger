import os
from typing import Annotated, Optional
from datetime import timedelta, datetime, timezone

import jwt
from sqlmodel import create_engine, SQLModel, Session
from fastapi import Depends
from fastapi.security import (
    OAuth2PasswordBearer,
)
from passlib.context import CryptContext


def create_db_engine():
    DB_PASSWORD = os.environ.get('MESSANGER_DB_PASSWORD')
    postgresql_url = f"postgresql://postgres:{DB_PASSWORD}@localhost:5432/messenger"

    connect_args = {}
    engine = create_engine(postgresql_url, connect_args=connect_args)

    return engine


engine = create_db_engine()


def create_db_and_tables(engine):
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


class Auth:
    _SECRET_KEY = "8227b96022bcb051d8b29834be2b23a5db1c47a3614bda615613152a36a48497"
    _ALGORITHM = "HS256"
    _ACCESS_TOKEN_EXPIRE_MINUTES = 1

    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.oauth2_scheme = OAuth2PasswordBearer(
            tokenUrl='login',
            scopes={
                'me': 'Read info about current user',
                'admin': 'You can do whatever you want',
                'supervisor': 'Chef of something important',
                'methodist': 'They pretend to be useful',
                'owner': 'They can only own their groups'
            }
        )

    def create_access_token(self, data: dict):
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(self._ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({'exp': expire})
        encoded_jwt = jwt.encode(to_encode, self._SECRET_KEY, algorithm=self._ALGORITHM)

        return encoded_jwt

auth_controller = Auth()
