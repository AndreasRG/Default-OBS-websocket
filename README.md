# Default OBS-websocket Service


## NOTE! See issues for current flaws in app!


## Overview
The **Default OBS-websocket** service acts as a Twitch → OBS → WebSocket bridge.  
It listens to Twitch chat messages, updates OBS sources, and broadcasts events to other services in a multi‑service environment.

This service can be used in three different ways:

### 1. Direct Python Execution  
You can run the service directly using Python.  
This is supported for development, but **not recommended** for production.

### 2. Single-Service Deployment via `docker-compose.yml`  
You can run the service as a standalone Docker container using Docker Compose.

### 3. Multi-Service Deployment  
The service can also be part of a larger microservice network.  
In this mode, the **Dockerfile** is used to build the service image, and `docker-compose.yml` orchestrates multiple services together.

---

## Required Configuration

Before running the service, you must update two configuration files located in:

/app/secret/

### 1. `server_websocket_info.json`
Contains OBS WebSocket connection details:

- OBS server IP  
- OBS WebSocket port  
- OBS WebSocket password  

Example:

```json
[
    {
        "server-ip": "your_obs_server_ip",
        "server-port": 4455,
        "server-password": "your_obs_server_password"
    }
]
```

### 2. `twitch_info.json`
Contains Twitch IRC authentication details:

- Twitch username
- OAuth token
- Channel name

Example:

```json
[
    {
        "username": "your_twitch_username",
        "auth_token": "your_twitch_bot_token - go to https://twitchtokengenerator.com/ , select 'Bot Chat Token' and sign in to create your token",
        "channel_name": "your_twitch_display_name"
    }
]
```

Make sure both files contain valid information before starting the service.

## OBS Setup (One-Time Requirement)

Before running this service, OBS must be configured to allow WebSocket connections:

1. Open **OBS Studio**
2. Navigate to **Tools → WebSocket Server Settings**
3. Enable the WebSocket server
4. Configure the following:
   - **Server port** (default: `4455`)
   - **Password**
5. Restart OBS if necessary

The service **cannot connect** until OBS WebSocket is enabled and running.

---

## Running the Service

### Python (Development Only)

```bash
python obs-websocket.py
```

### Docker Compose (Single Service)

```bash
docker compose up --build
```

### Docker Compose (Multi-Service Network)

Include this service inside a larger architecture and reference it in docker-compose.yml:

```yaml
services:
  obs-websocket:
    build: ./websocket-service
    restart: unless-stopped
```

Other services can connect to the broadcast WebSocket via:

```code
ws://obs-websocket:8000
```

## What This Service Provides

- Twitch chat listener
- OBS WebSocket controller
- Real-time WebSocket broadcast server
- Event distribution to other services
- Docker-ready architecture

This service acts as the central event hub for your Twitch-driven system.
