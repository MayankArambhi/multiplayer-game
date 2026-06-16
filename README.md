# Multiplayer Fighting Game
(Fighting logic is yet to be implemented)

This is a **simple-2D-openWorld-multiplayer-game** made using **Python**, **Pygame**, **FastAPI** and **WebSockets**.

## Features

- Multiplayer support
- Real-time player movement
- JSON based client-server communication
- Music and sound effects
- Latency measurement
- Scalable

## Upcoming Features

- Health pickups
- Weapons
- Damage/Fighting logic
- Scoreboard
- Game Over screen

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
- Install dependencies:
```text
pip install fastapi uvicorn pygame websocket-client
```

- Start the server:
```text
python -m uvicorn server:app --host 0.0.0.0 --port 8000 --reload
```

- Run in one terminal:
```text
python -m game.py
```

- Open another terminal(use different name):
```text
python -m game.py
```