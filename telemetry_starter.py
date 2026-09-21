import json
import socket
import sys
from collections import deque

from websocket import WebSocketApp

WS_URL = "ws://127.0.0.1:8080" #where we are listening for JSON
UDP_PORT = 20777 #receiver port
RECONNECT_SECONDS = 5
recent_packets = deque(maxlen=100) #most recent 100 json packets

#finds the current IP address of the machine to display to the user (used to tell ps4 where to send udp)
def get_current_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("10.255.255.255", 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = "127.0.0.1"
    finally:
        s.close()
    return IP

#parses json, adds them to the deque, prints the type of packet and the current size of the deque (window)
def on_message(ws, message):
    try:
        packet = json.loads(message)
    except json.JSONDecodeError:
        print("[ERR] Skipping non-JSON payload", flush=True)
        return
    recent_packets.append(packet)
    packet_type = packet.get("type", "UNKNOWN")
    print(f"[OK] {packet_type} | window={len(recent_packets)}", flush=True)

#logging callbacks for websocket events
def on_open(ws):
    print(f"Listening on {WS_URL}", flush=True)

def on_error(ws, error):
    print(f"[ERR] WebSocket: {error}", flush=True)


def on_close(ws, close_status_code, close_msg):
    print(
        f"Disconnected (code={close_status_code}). "
        f"Reconnecting in {RECONNECT_SECONDS}s...",
        flush=True,
    )


def main():
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass

#prints instructions (ip and upd port)
    IP_LOCAL = get_current_ip()
    print("=" * 55)
    print("Starting telemetry client...")
    print("=" * 55)
    print(" VERIFY THE FOLLOWING DATA IN PS4")
    print(f" -> IP address of UDP transmission: {IP_LOCAL}")
    print(f" -> UDP transmission port:       {UDP_PORT}")
    print("=" * 55)
    print(f"Listening constantly for JSON on {WS_URL}\n")

    #create ws app and run it forever, reconnecting if the collector restarts or drops
    ws = WebSocketApp(
        WS_URL,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
    )
    # Blocks forever; reconnects when the collector restarts or drops.
    ws.run_forever(reconnect=RECONNECT_SECONDS)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nClient closed correctly")
