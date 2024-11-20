from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.internal.utils import websocket_manager, SessionDep
from app.controllers.messages import save_message

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
            message = save_message(session=session, message=message)
            await websocket_manager.send_message(room_id=room_id, message=message)
    except WebSocketDisconnect:
        websocket_manager.disconnect(room_id=room_id, username=username)
