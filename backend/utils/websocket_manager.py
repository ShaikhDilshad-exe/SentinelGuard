import logging
from fastapi import WebSocket
import json
from typing import List

logger = logging.getLogger(__name__)

class WebSocketManager:
    """Manages active WebSocket connections."""
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Accepts and stores a new WebSocket connection."""
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        """Closes and removes a WebSocket connection."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        """Sends a JSON message to all active clients."""
        # Iterate over a copy of the list to safely handle disconnections during broadcast
        for connection in list(self.active_connections):
            try:
                await connection.send_json(message)
            except Exception:
                # If sending fails, assume the client has disconnected and remove them.
                self.disconnect(connection)

# Create a single, shared instance of the manager
manager = WebSocketManager()