from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import json
from websocketManager import ConnectionManager
import random
import numpy as np
def dist(x1,y1,x2,y2):
    return int(np.sqrt((x1-x2)**2 + (y1-y2)**2))

app = FastAPI()
manager = ConnectionManager()

class Ball:
    def __init__(self, name: str, pos_x: int, pos_y: int):
        self.name = name
        self.vel_x = 0
        self.vel_y = 0
        self.health = 5
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.status = None # equip weapon, health regain, dead, damage opponent
        self.event = None

    def move(self, keys):
        global WIDTH
        global HEIGHT
        ACCEL = 0.5
        FRICTION = 0.98
        MAX_SPEED = 6
        if keys.get("up"):
            self.vel_y -= ACCEL
        if keys.get("down"):
            self.vel_y += ACCEL
        if keys.get("left"):
            self.vel_x -= ACCEL
        if keys.get("right"):
            self.vel_x += ACCEL

        self.vel_x = max(-MAX_SPEED,min(MAX_SPEED, self.vel_x))
        self.vel_y = max(-MAX_SPEED,min(MAX_SPEED, self.vel_y))

        self.pos_x += self.vel_x
        self.pos_y += self.vel_y

        self.pos_x = max(20,min(WIDTH-20,self.pos_x))
        self.pos_y = max(20,min(HEIGHT-20,self.pos_y))

        self.vel_x *= FRICTION
        self.vel_y *= FRICTION

    def attack(self):
        global Obj, players
        for player in players.keys():
            if player != self.name and dist(players[player].pos_x, players[player].pos_y, self.pos_x, self.pos_y) <= 40 and self.status=="Knife equipped" and players[player].health > 0:
                players[player].health -= 1
                players[player].event = "Damage received"
                self.status = None
                Obj = {"Knife": Collective("Knife", random.randint(20,WIDTH), random.randint(20,HEIGHT), damage=1, isTaken=False)}

    def markstatus(self, statusName: str = None):
        self.status = statusName

class Collective: # health pickup, weapons
    def __init__(self, name: str, pos_x: int, pos_y: int, damage: int, isTaken: bool = False):
        self.name = name
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.damage = damage
        self.isTaken = isTaken

    def findBearer(self, players: dict):
        for player in players.keys():
            if np.sqrt((players[player].pos_x - self.pos_x) ** 2 + (players[player].pos_y - self.pos_y) ** 2) < 35 and players[player].health > 0:
                players[player].markstatus("Knife equipped")
                self.pos_x, self.pos_y = players[player].pos_x, players[player].pos_y
                self.isTaken = True
                break

WIDTH, HEIGHT = 800, 600
players = {}
Obj = {"Knife": Collective("Knife", random.randint(20,WIDTH), random.randint(20,HEIGHT), damage=1, isTaken=False)}
messages = []

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
                "status": player.status,
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
        },
        "messages": messages
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    global messages
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
            message = data.get("message")
            if message:
                messages.append({"sender": player_name, "message": message})
            messages = messages[-20:]

            if not player_name:
                continue

            if player_name not in players:
                players[player_name] = Ball(
                    name=player_name,
                    pos_x=100 + len(players) * 60,
                    pos_y=100
                )
                manager.register(websocket, player_name)

            players[player_name].event = None
            players[player_name].move(keys)
            players[player_name].attack()
            for object in Obj:
                Obj[object].findBearer(players)
            if players[player_name].health <= 0:
                players[player_name].markstatus("Dead")
            if keys.get("restart") and players[player_name].status == "Dead":
                players[player_name].pos_x = random.randint(20,WIDTH-20)
                players[player_name].pos_y = random.randint(20,HEIGHT-20)
                players[player_name].status = None
                players[player_name].health = 5

            await websocket.send_json(make_world_state())

    except WebSocketDisconnect:
        manager.disconnect(websocket)

        if player_name in players:
            if players[player_name].status == "Knife equipped":
                Obj["Knife"].isTaken = False
            del players[player_name]