# Functions to establishing connections:
import json
import socket
from obswebsocket import obsws, requests
import asyncio
import urllib.parse
import websockets



# WebSocket broadcast service

global_obs_ws = None

clients = set()

async def handle_command(msg):
    try:
        data = json.loads(msg)
    except:
        print("Invalid JSON command received")
        return

    # Example command: update OBS input
    if data.get("type") == "set_input":
        input_name = data.get("inputName")
        input_settings = data.get("inputSettings")

        if global_obs_ws:
            global_obs_ws.call(requests.SetInputSettings(
                inputName=input_name,
                inputSettings=input_settings,
                overlay=False
            ))
            print(f"Updated OBS input: {input_name}")


async def ws_handler(ws):
    clients.add(ws)
    try:
        async for msg in ws:
            await handle_command(msg)
    finally:
        clients.remove(ws)

async def broadcast_event(event):
    # event is a dict: {"username": ..., "message": ...}
    data = json.dumps(event)
    for ws in clients:
        await ws.send(data)

async def start_ws_server():
    async with websockets.serve(ws_handler, "0.0.0.0", 8000):
        await asyncio.Future()


# Twitch chat service

def twitch_chat_listener(ws):
    with open("./secret/twitch_info.json", "r") as f:
        twitch_data = json.load(f)[0]

    server = "irc.chat.twitch.tv"
    port = 6667
    nickname = twitch_data["username"].lower()
    token = "oauth:" + twitch_data["auth_token"]
    channel = twitch_data["channel_name"].lower()

    sock = socket.socket()
    sock.connect((server, port))
    sock.send(f"PASS {token}\r\n".encode("utf-8"))
    sock.send(f"NICK {nickname}\r\n".encode("utf-8"))
    sock.send(f"CAP REQ :twitch.tv/tags\r\n".encode("utf-8"))
    sock.send(f"JOIN #{channel}\r\n".encode("utf-8"))

    print("Connected to Twitch chat!")

    while True:
        resp = sock.recv(2048).decode("utf-8")

        for line in resp.split("\r\n"):
            if not line:
                continue

            print("RAW:", line)

            if line.startswith("PING"):
                sock.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
                continue

            if "PRIVMSG" in line:
                # Extract IRC tags (metadata)
                tags_part = line.split(" ", 1)[0]

                tags = {}
                if tags_part.startswith("@"):
                    for tag in tags_part[1:].split(";"):
                        key, value = tag.split("=", 1)
                        tags[key] = value

                display_name = tags.get("display-name", None)

                # Fallback if display-name is missing
                if not display_name:
                    display_name = line.split("!", 1)[0][1:]

                # Extract message
                message = line.split("PRIVMSG", 1)[1].split(":", 1)[1]

                print("Display name:", display_name)
                print("Message:", message)

                text = f"{display_name}: {message}"
                # encoded_text = urllib.parse.quote(text)

                ws.call(requests.SetInputSettings(
                    inputName="Latest Chat Message",
                    inputSettings={"text": text},
                    overlay=False
                ))


                # Broadcast event to WebSocket clients
                event = {
                    "username": display_name,
                    "message": message
                }
                asyncio.run(broadcast_event(event))





# OBS service

def obs_connect():
    with open("./secret/server_websocket_info.json", "r") as f:
        websocket_data = json.load(f)[0]

    ip = websocket_data["server-ip"]
    port = websocket_data["server-port"]
    password = websocket_data["server-password"]

    ws = obsws(ip, port, password)
    ws.connect()

    print(ws.call(requests.GetVersion()))
    print("OBS connected successfully!")

    return ws
