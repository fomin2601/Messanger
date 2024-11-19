from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.internal.utils import websocket_manager

router = APIRouter(
    prefix='/messages',
    tags=['messages']
)


@router.websocket('/{room_id}/ws')
async def message_exchange(websocket: WebSocket, room_id: int, username: str):
    await websocket_manager.connect(room_id=room_id, username=username, websocket=websocket)
    try:
        while True:
            message = await websocket.receive_json()
            await websocket_manager.send_message(room_id=room_id, message=message)
    except WebSocketDisconnect:
        websocket_manager.disconnect(room_id=room_id, username=username)
