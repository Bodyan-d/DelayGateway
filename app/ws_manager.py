from typing import Dict, List
from fastapi import WebSocket
import asyncio
import json

class ConnectionManager:
    def __init__(self):
        # key: topic or user_id -> list of websockets
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self.lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket, topic: str = "global"):
        await websocket.accept()
        async with self.lock:
            self.active_connections.setdefault(topic, []).append(websocket)

    async def disconnect(self, websocket: WebSocket):
        async with self.lock:
            for topic, conns in list(self.active_connections.items()):
                if websocket in conns:
                    conns.remove(websocket)
                    if len(conns) == 0:
                        del self.active_connections[topic]

    async def broadcast(self, message: dict, topic: str = "global"):
        data = json.dumps(message, default=str)
        async with self.lock:
            conns = list(self.active_connections.get(topic, []))
        for conn in conns:
            try:
                await conn.send_text(data)
            except Exception:
                # ignore errors; ideally log
                pass

ws_manager = ConnectionManager()
