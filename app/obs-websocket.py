import sys
import threading
import time
from obswebsocket import obsws, requests
import connection
import asyncio

def main():
    try:
        # Connect to OBS
        ws = connection.obs_connect()

        # Start Twitch chat listener in a thread
        twitch_thread = threading.Thread(
            target=connection.twitch_chat_listener,
            args=(ws,),
            daemon=True
        )
        twitch_thread.start()

        # Start WebSocket server in a thread
        ws_server_thread = threading.Thread(
            target=lambda: asyncio.run(connection.start_ws_server()),
            daemon=True
        )
        ws_server_thread.start()

        connection.global_obs_ws = ws

        print("System running...")

        # Block main thread without burning CPU
        try:
            twitch_thread.join()
            ws_server_thread.join()
        except KeyboardInterrupt:
            print("Shutting down...")

        ws.disconnect()
        print("Shutdown complete.")

    except Exception as e:
        print("Error:", e)
        print("Code failure, aborting program...")
        sys.exit()

if __name__ == "__main__":
    main()
