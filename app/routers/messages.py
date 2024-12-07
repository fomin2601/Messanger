from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status, Depends
from typing import List
from app.internal.utils import websocket_manager, websocket_keys_exchange_manager, SessionDep, JWTBearer
from app.controllers import messages
from app.schemes.messages import MessageScheme

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


@router.get(
    '/{room_id}',
    status_code=status.HTTP_200_OK,
    response_model=List[MessageScheme],
    dependencies=[Depends(JWTBearer())]
)
async def get_room_messages(session: SessionDep, room_id: int):
    room_messages = messages.get_room_messages(session=session, room_id=room_id)

    return room_messages


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
                #public_rsa_key = data['public_rsa_key']
                await websocket_keys_exchange_manager.send_superuser_key_to_user(
                    target_user_id=target_user_id,
                    data=data
                )

            else:
                #aes_key = data['aes_key']
                await websocket_keys_exchange_manager.send_user_key_to_superuser(
                    target_superuser_id=target_user_id,
                    data=data
                )

    except WebSocketDisconnect:
        if is_superuser:
            websocket_keys_exchange_manager.superuser_disconnect(room_id=room_id, superuser_id=user_id)

        else:
            websocket_keys_exchange_manager.user_disconnect(room_id=room_id, user_id=user_id)
