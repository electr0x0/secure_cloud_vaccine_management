import asyncio
import json
from fastapi import WebSocket
from src.core.logger import get_logger
from src.core.config import settings

logger = get_logger(__name__)

class WSManager:
    def __init__(self):
        self.connections = []
        self._ping_task = None

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.connections.append(websocket)
        logger.info(f"New WebSocket connection. Total: {len(self.connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.connections:
            self.connections.remove(websocket)
            logger.info(f"WebSocket disconnected. Remaining: {len(self.connections)}")

    async def broadcast(self, message: str):
        disconnected = []
        for conn in self.connections[:]:
            try:
                await conn.send_text(message)
            except Exception as e:
                logger.error(f"Failed to send message: {str(e)}")
                disconnected.append(conn)
        
        for conn in disconnected:
            self.disconnect(conn)

    async def broadcast_log(self, message: str):
        await self.broadcast(json.dumps({
            "type": "log",
            "message": message
        }))

    async def ping_loop(self):
        while True:
            await asyncio.sleep(settings.WEBSOCKET_PING_INTERVAL)
            if self.connections:
                await self.broadcast(json.dumps({"type": "ping"}))

manager = WSManager() 