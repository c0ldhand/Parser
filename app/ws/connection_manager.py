from datetime import datetime
from typing import List
from fastapi import WebSocket
from uuid import UUID
import json
from app.schemas.currency import CurrencyRateOut
from app.schemas.ws_events import CurrencyEvent, CurrencyEventType

class ConnectionManager:
    """Управление активными WS-соединениями и broadcast сообщений."""

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Принять новое соединение WebSocket."""
        await websocket.accept()
        self.active_connections.append(websocket)

    async def disconnect(self, websocket: WebSocket):
        """Отключить WebSocket соединение."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, event: CurrencyEvent):
        """Отправить событие всем подключённым клиентам."""
        if not self.active_connections:
            return

        message = event.model_dump_json()
        disconnected = []

        for websocket in list(self.active_connections):
            try:
                await websocket.send_text(message)
            except Exception:
                disconnected.append(websocket)

        for ws in disconnected:
            await self.disconnect(ws)


manager = ConnectionManager()