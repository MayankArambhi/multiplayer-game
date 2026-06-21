# Multiplayer Fighting Game
(Fighting mechanics JUST implemented)

This is a **simple-2D-openWorld-multiplayer-game** made using **Python**, **Pygame**, **FastAPI** and **WebSockets**.

## Features

- Real-time player movement
- JSON based client-server communication
- Music and sound effects
- Multiplayer support
- Latency measurement
- Scalable

### New

- Game over screen
- Fighting mechanism

## Upcoming Features

- Health pickups
- Scoreboard

## Components
### Client (game.py)

- Sends keyboard inputs to server in form of JSON.
- Receives player/object position, health and other attributes.
- Draws everything in PyGame window.

### Server (Backend/server.py)

- Stores all the clients that are connected.
- Accepts keyboard input.
- Does all the computations and updates the game/world state.
- Sends JSON data to all clients.

### WebSocket Manager (Backend/websocketManager.py)

- The bridge connecting clients and server.

### Timer (Backend/_timer.py)

- Used to measure latency.

## Tech Stack

- Python
- Pygame
- FastAPI
- WebSockets
- JSON

## Project Structure

```text
.
├── game.py
├── README.md
├── Backend/
|   ├── websocketManager.py
|   ├── _timer.py
|   └── server.py
├── Schema/
|   ├── Client-Server.json
|   └── Server-Client.json
└── Assets/
    ├── bg.wav
    ├── bounce.wav
    └── damage.wav
```

## How to Run:
### install dependencies
```text
pip install fastapi uvicorn pygame websocket-client
```

### Start the server in terminal
```text
cd Backend
python -m uvicorn server:app --host 0.0.0.0 --port 8000 --reload
```

### Terminal 2
```text
python -m game.py
```
- Use IPV4 addres **127.0.0.1** if you are running it locally. 
- Otherwise:
```
ipcofig
```
- Copy IPV4 address.

### Terminal 3
```text
python -m game.py
```

## Playing multiplayer over internet
- Use VPN like Hamachi or Radmin, connect all devices.
- Or use Port forwarding if available.