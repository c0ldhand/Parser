from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.ws.connection_manager import manager

router = APIRouter()

@router.websocket("/ws/currencies")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket для уведомлений о курсах валют"""
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
    except Exception as e:
        await manager.disconnect(websocket)