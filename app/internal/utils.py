import os
from typing import Annotated, Dict, Tuple, List
import time

import jwt
from sqlmodel import create_engine, SQLModel, Session, inspect, insert
from fastapi import Depends, Request, HTTPException, WebSocket
from fastapi.security import (
    HTTPBearer,
    HTTPAuthorizationCredentials
)
from passlib.context import CryptContext
from app.models.messages import Message
from app.schemes.messages import RSAScheme, AESScheme
from app.config import predefined_tables


def create_db_engine():
    DB_PASSWORD = os.environ.get('MESSENGER_DB_PASSWORD')
    postgresql_url = f"postgresql://postgres:{DB_PASSWORD}@localhost:5432/messenger"

    connect_args = {}
    engine = create_engine(postgresql_url, connect_args=connect_args)

    return engine


engine = create_db_engine()


def create_db_and_tables(engine):
    tables_to_predefine = [table for table in predefined_tables.keys() if not inspect(engine).has_table(table)]
    SQLModel.metadata.create_all(engine)
    return tables_to_predefine


def predefine_tables(engine, tables):
    if tables:
        with engine.connect() as connection:
            for table in tables:
                connection.execute(
                    insert(SQLModel.metadata.tables[table]),
                    predefined_tables[table]
                )
                connection.commit()


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


class WebsocketConnectionManager:
    def __init__(self):
        self.active_connections: Dict[Tuple[int, str], WebSocket] = {}
        self.rooms: Dict[int, List[str]] = {}

    async def connect(self, room_id: int, username: str, websocket: WebSocket):
        websocket_uid = (room_id, username)
        await websocket.accept()
        self.active_connections[websocket_uid] = websocket
        self.add_user_to_room(room_id=room_id, username=username)

    def disconnect(self, room_id: int, username: str):
        websocket_uid = (room_id, username)
        self.rooms[room_id].remove(username)
        self.active_connections.pop(websocket_uid)

    async def send_message(self, room_id: int, message: Message):
        room_connections = self.rooms.get(room_id, None)
        #TODO: Заменить на MessageScheme
        data = {
            'message': message.model_dump(),
            'sender': message.sender.model_dump()
        }

        if room_connections is None:
            pass
        else:
            for user_connection in room_connections:
                websocket_uid = (room_id, user_connection)
                await self.active_connections[websocket_uid].send_json(data)

    def add_user_to_room(self, room_id: int, username: str):
        room = self.rooms.get(room_id, None)

        if room is None:
            self.rooms[room_id] = [username]

        else:
            self.rooms[room_id].append(username)


websocket_manager = WebsocketConnectionManager()


class KeysExchangeWebsocketManager:
    def __init__(self):
        self.room_superuser_connections: Dict[Tuple[int, int], WebSocket] = {}
        self.room_user_connections: Dict[Tuple[int, int], WebSocket] = {}

    async def superuser_connect(self, room_id: int,  superuser_id: int, websocket: WebSocket):
        websocket_uid = (room_id, superuser_id)
        await websocket.accept()
        self.room_superuser_connections[websocket_uid] = websocket

    def superuser_disconnect(self, room_id: int,  superuser_id: int):
        websocket_uid = (room_id, superuser_id)
        self.room_superuser_connections.pop(websocket_uid)

    async def user_connect(self, room_id: int, user_id: int, websocket: WebSocket):
        websocket_uid = (room_id, user_id)
        await websocket.accept()
        self.room_user_connections[websocket_uid] = websocket

    def user_disconnect(self, room_id: int, user_id: int):
        websocket_uid = (room_id, user_id)
        self.room_user_connections.pop(websocket_uid)

    async def send_user_key_to_superuser(self, room_id: int, target_superuser_id: int, data: Dict):
        websocket_uid = (room_id, target_superuser_id)
        target_websocket = self.room_superuser_connections.get(websocket_uid, None)

        if target_websocket is not None:
            await target_websocket.send_json(data)

        else:
            #TODO: Посмотреть, как ожидать коннекта пользователя
            pass

    async def send_superuser_key_to_user(self, room_id: int, target_user_id: int, data: Dict):
        websocket_uid = (room_id, target_user_id)
        target_websocket = self.room_superuser_connections.get(websocket_uid, None)

        if target_websocket is not None:
            await target_websocket.send_json(data)

        else:
            # TODO: Посмотреть, как ожидать коннекта пользователя
            pass


websocket_keys_exchange_manager = KeysExchangeWebsocketManager()
