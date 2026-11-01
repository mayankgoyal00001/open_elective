"""
WebSocket Connection Manager
Handles real-time streaming of simulation state, telemetry, and safety alerts
to connected frontend client dashboards.
"""
import asyncio
import json
from typing import List, Set
from fastapi import WebSocket, WebSocketDisconnect

class WebSocketManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)

    async def broadcast_state(self, state_dict: dict):
        if not self.active_connections:
            return

        payload = json.dumps(state_dict)
        dead_connections = []

        for conn in self.active_connections:
            try:
                await conn.send_text(payload)
            except Exception:
                dead_connections.append(conn)

        for dead in dead_connections:
            self.disconnect(dead)

ws_manager = WebSocketManager()
