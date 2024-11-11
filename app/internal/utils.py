import os
from typing import Annotated, Optional
import time

import jwt
from sqlmodel import create_engine, SQLModel, Session
from fastapi import Depends, Request, HTTPException
from fastapi.security import (
    HTTPBearer,
    HTTPAuthorizationCredentials
)
from passlib.context import CryptContext


def create_db_engine():
    DB_PASSWORD = os.environ.get('MESSENGER_DB_PASSWORD')
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
    _SECRET_KEY = os.environ.get('MESSENGER_SECRET_KEY')
    _ALGORITHM = "HS256"
    _ACCESS_TOKEN_EXPIRE_MINUTES = 24*60*7

    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def create_jwt(self, data: dict):
        to_encode = data.copy()
        expire = time.time() + self._ACCESS_TOKEN_EXPIRE_MINUTES * 60
        to_encode.update({'exp': expire})
        encoded_jwt = jwt.encode(to_encode, self._SECRET_KEY, algorithm=self._ALGORITHM)

        return encoded_jwt

    def decode_jwt(self, token):
        payload = jwt.decode(token, self._SECRET_KEY, algorithms=[self._ALGORITHM])
        username: str = payload.get('sub', None)
        expired = payload.get('exp', None)
        print(username, expired > time.time(), expired - time.time())

        if username is None or expired is None:
            return None

        if expired < time.time():
            return None

        return payload


auth_controller = Auth()


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == 'Bearer':
                raise HTTPException(status_code=403, detail='Invalid authentication scheme')
            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(status_code=403, detail='Either token invalid or expired')
            return credentials.credentials
        else:
            raise HTTPException(status_code=403, detail='Invalid authorization code')

    @staticmethod
    def verify_jwt(jwtoken: str) -> bool:
        is_token_valid: bool = False

        try:
            payload = auth_controller.decode_jwt(jwtoken)
        except:
            payload = None

        if payload:
            is_token_valid = True

        return is_token_valid
