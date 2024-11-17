from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

from app.internal.utils import JWTBearer, SessionDep, websocket_manager

router = APIRouter(
    prefix='/messages',
    tags=['messages'],
    dependencies=[Depends(JWTBearer())]
)

@router.websocket('/{room_id}/ws')
async def message_exchange(
        *,
        websocket: WebSocket,
        room_id: int,
        session: SessionDep,
):
    await websocket_manager.connect(websocket)
    try:
        while True:
            message = await websocket.receive_json()
            await websocket_manager.send_message(message)
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)