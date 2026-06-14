from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import json

from websocketManager import ConnectionManager

app = FastAPI()
manager = ConnectionManager()

WIDTH, HEIGHT = 800, 600
players = {}

class Ball:
    def __init__(self, name: str, speed: int = 5, health: int = 5, pos_x: int = 100, pos_y: int = 100):
        self.name = name
        self.speed = speed
        self.health = health
        self.pos_x = pos_x
        self.pos_y = pos_y

    def move(self, keys):
        if keys.get("up"):
            self.pos_y -= self.speed
        if keys.get("down"):
            self.pos_y += self.speed
        if keys.get("left"):
            self.pos_x -= self.speed
        if keys.get("right"):
            self.pos_x += self.speed

        self.pos_x = max(20, min(WIDTH - 20, self.pos_x))
        self.pos_y = max(20, min(HEIGHT - 20, self.pos_y))

@app.get("/")
def home():
    return {"msg": "Server running"}

def make_world_state():
    return {
        "screenSize": {
            "height": HEIGHT,
            "width": WIDTH
        },
        "entities": {
            name: {
                "pos_x": player.pos_x,
                "pos_y": player.pos_y,
                "health": player.health
            }
            for name, player in players.items()
        },
        "objects": {}
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)

    player_name = None

    try:
        while True:
            text = await websocket.receive_text()

            try:
                data = json.loads(text)
            except json.JSONDecodeError:
                continue

            player_name = data.get("name")
            keys = data.get("keysPressed", {})

            if not player_name:
                continue

            if player_name not in players:
                players[player_name] = Ball(
                    name=player_name,
                    pos_x=100 + len(players) * 60,
                    pos_y=100
                )
                manager.register(websocket, player_name)

            players[player_name].move(keys)

            await websocket.send_json(make_world_state())

    except WebSocketDisconnect:
        manager.disconnect(websocket)

        if player_name in players:
            del players[player_name]