from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
        self.ws_to_id: dict = {}
        self.id_to_ws: dict = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if websocket in self.ws_to_id:
            cid = self.ws_to_id.pop(websocket)
            self.id_to_ws.pop(cid, None)

    def register(self, websocket: WebSocket, client_id: str):
        self.ws_to_id[websocket] = client_id
        self.id_to_ws[client_id] = websocket

    async def broadcast(self, data: dict):
        dead_connections = []

        for connection in self.active_connections:
            try:
                await connection.send_json(data)
            except:
                dead_connections.append(connection)

        for connection in dead_connections:
            self.disconnect(connection)