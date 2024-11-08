import multiprocessing
from multiprocessing import Manager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

class WSConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, client_id: str, websocket: WebSocket):
        await websocket.accept()
        if client_id in self.active_connections:
            await self.active_connections.pop(client_id).close()
        self.active_connections[client_id] = websocket

    def disconnect(self, client_id: str, websocket: WebSocket):
        self.active_connections.pop(client_id)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections.values():
            await connection.send_text(message)


ws_manager = WSConnectionManager()
