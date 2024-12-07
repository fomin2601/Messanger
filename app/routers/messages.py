from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status, Depends
from typing import List
from app.internal.utils import websocket_manager, websocket_keys_exchange_manager, SessionDep, JWTBearer
from app.controllers import messages
from app.models.messages import MessageScheme

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
