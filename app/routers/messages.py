from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status, Depends, File
from fastapi.responses import Response
from typing import List, Annotated
from app.internal.utils import websocket_manager, websocket_keys_exchange_manager, SessionDep, JWTBearer
from app.controllers import messages
from app.schemes.messages import MessageScheme
from app.internal.s3 import s3_handler


router = APIRouter(
    prefix='/messages',
    tags=['messages']
)


@router.websocket('/{room_id}/ws')
async def message_exchange(websocket: WebSocket, session: SessionDep, room_id: int, username: str):
    await websocket_manager.connect(room_id=room_id, username=username, websocket=websocket)
    try:
        while True:
            message = await websocket.receive_json()
            message['room_id'] = room_id
            message = messages.save_message(session=session, message=message)
            await websocket_manager.send_message(room_id=room_id, message=message)
    except WebSocketDisconnect:
        websocket_manager.disconnect(room_id=room_id, username=username)


@router.websocket('/{room_id}/keys_exchange/ws')
async def keys_exchange(websocket: WebSocket, room_id: int, user_id: int, is_superuser: bool):
    if is_superuser:
        await websocket_keys_exchange_manager.superuser_connect(
            room_id=room_id,
            superuser_id=user_id,
            websocket=websocket
        )

    else:
        await websocket_keys_exchange_manager.user_connect(
            room_id=room_id,
            user_id=user_id,
            websocket=websocket
        )

    try:
        while True:
            data = await websocket.receive_json()
            target_user_id = data['target_user_id']
            if is_superuser:
                await websocket_keys_exchange_manager.send_superuser_key_to_user(
                    room_id=room_id,
                    target_user_id=target_user_id,
                    data=data
                )

            else:
                await websocket_keys_exchange_manager.send_user_key_to_superuser(
                    room_id=room_id,
                    target_superuser_id=target_user_id,
                    data=data
                )

    except WebSocketDisconnect:
        if is_superuser:
            websocket_keys_exchange_manager.superuser_disconnect(room_id=room_id, superuser_id=user_id)

        else:
            websocket_keys_exchange_manager.user_disconnect(room_id=room_id, user_id=user_id)


@router.get(
    '/{room_id}',
    status_code=status.HTTP_200_OK,
    response_model=List[MessageScheme],
    dependencies=[Depends(JWTBearer())]
)
async def get_room_messages(session: SessionDep, room_id: int):
    room_messages = messages.get_room_messages(session=session, room_id=room_id)

    return room_messages


class RawResponse(Response):
    media_type = "binary/octet-stream"

    def render(self, content: bytes) -> bytes:
        return bytes([b ^ 0x54 for b in content])


@router.get(
    '/attachments/{file_id}',
    status_code=status.HTTP_200_OK,
    #dependencies=[Depends(JWTBearer())]
)
def download_file(session: SessionDep, file_id: str):
    file_bytes = s3_handler.download_file_from_s3(file_id=file_id)
    return Response(content=file_bytes, media_type='application/octet-stream')


@router.post('/attachments/{file_id}')
def upload_file(session: SessionDep, file_id: str, file: Annotated[bytes, File()]):
    s3_handler.upload_file_to_s3(bytes(file), file_id)

