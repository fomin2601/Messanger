from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status
from typing import List
from app.internal.utils import websocket_manager, SessionDep
from app.controllers import messages
from app.models.messages import MessageScheme

router = APIRouter(
    prefix='/messages',
    tags=['messages']
)


@router.websocket('/{room_id}/ws')
async def message_exchange(websocket: WebSocket, room_id: int, username: str, session: SessionDep):
    await websocket_manager.connect(room_id=room_id, username=username, websocket=websocket)
    try:
        while True:
            message = await websocket.receive_json()
            message['room_id'] = room_id
            message = messages.save_message(session=session, message=message)
            await websocket_manager.send_message(room_id=room_id, message=message)
    except WebSocketDisconnect:
        websocket_manager.disconnect(room_id=room_id, username=username)


@router.get('/{room_id}', status_code=status.HTTP_200_OK, response_model=List[MessageScheme])
async def get_room_messages(session: SessionDep, room_id: int):
    room_messages = messages.get_room_messages(session=session, room_id=room_id)

    return room_messages
