from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import json
from websocketManager import ConnectionManager
import random
import numpy as np

app = FastAPI()
manager = ConnectionManager()

class Ball:
    def __init__(self, name: str, speed: int = 5, health: int = 5, pos_x: int = 100, pos_y: int = 100, event: str = None):
        self.name = name
        self.speed = speed
        self.health = health
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.event = event # equip weapon, health regain, dead, damage opponent

    def move(self, keys):
        global WIDTH
        global HEIGHT
        if keys.get("up") and self.pos_y >= 20:
            self.pos_y -= self.speed
        if keys.get("down") and self.pos_y <= HEIGHT - 20:
            self.pos_y += self.speed
        if keys.get("left") and self.pos_x >= 20:
            self.pos_x -= self.speed
        if keys.get("right") and self.pos_x <= WIDTH - 20:
            self.pos_x += self.speed

    def markEvent(self, eventName: str = None):
        self.event = eventName
class Collective: # health pickup, weapons
    def __init__(self, name: str, pos_x: int, pos_y: int, damage: int, isTaken: bool = False):
        self.name = name
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.damage = damage
        self.isTaken = isTaken

    def findBearer(self, players: dict):
        for player in players.keys():
            if np.sqrt((players[player].pos_x - self.pos_x) ** 2 + (players[player].pos_y - self.pos_y) ** 2) < 30:
                if self.damage > 0:
                    players[player].markEvent("Knife equipped")
                    self.pos_x, self.pos_y = players[player].pos_x, players[player].pos_y
                    self.isTaken = True 
                break

WIDTH, HEIGHT = 800, 600
players = {}
Obj = {"Knife": Collective("Knife", random.randint(0,WIDTH), random.randint(0,HEIGHT), damage=1, isTaken=False)}

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
                "health": player.health,
                "event": player.event
            }
            for name, player in players.items()
        },
        "objects": {
            name: {
                "pos_x": obj.pos_x,
                "pos_y": obj.pos_y,
                "isTaken": obj.isTaken
            }
            for name, obj in Obj.items()
        }
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
            for object in Obj:
                Obj[object].findBearer(players)

            await websocket.send_json(make_world_state())

    except WebSocketDisconnect:
        manager.disconnect(websocket)

        if player_name in players:
            del players[player_name]