# SafeChat

> AI-Powered Cyberbullying Detection Chat System

## Features
- Real-time AI moderation with LinearSVC model
- Multi-room TCP chat — join rooms by ID
- File sharing between users
- Dual client: CLI terminal + Tkinter GUI
- Fully Dockerised with Alpine multi-stage builds
- Non-root containers for security
- Zero hardcoded paths — all config via env vars

## Quick Start (Docker)

```bash
# 1. Build images
docker compose build

# 2. Start server
docker compose up -d server

# 3. Connect a client (open new terminal per user)
docker compose run --rm client
```

## Local Run (no Docker)

```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
# Terminal 1
python server/server.py
# Terminal 2 (new tab per user)
python client/client.py
```

## Make Commands

```
make build    Build Docker images
make up       Start server detached
make client   Connect CLI client
make logs     Follow server logs
make down     Stop containers
make rebuild  Full no-cache rebuild
make clean    Remove images and volumes
```

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| SERVER_HOST | 0.0.0.0 | Bind address |
| SERVER_PORT | 12345 | TCP port |
| MODELS_DIR | /app/models | Path to .pkl files |

## Project Structure

```
SafeChat/
server/server.py       TCP server with ML detection
client/client.py       CLI client
client/client_gui.py   Tkinter GUI client
models/                Pre-trained model files
Dockerfile.server      Alpine multi-stage server
Dockerfile.client      Alpine multi-stage client
docker-compose.yml     Orchestration
requirements.txt       Pinned dependencies
Makefile               Dev commands
```

## How AI Moderation Works

Every message is vectorised with TF-IDF (Hinglish stopwords) then
classified by a LinearSVC model. Bullying messages are blocked
client-side and hidden server-side — they never reach other users.

## Author

Suhail Saifi - https://github.com/suhailsaifi
