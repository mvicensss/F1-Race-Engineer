import asyncio
import json
from collections import deque

import websockets

# Shared short-term memory for AI agents (FIFO, most recent 100 frames).
telemetry_buffer = deque(maxlen=100)

#
async def collect_data():
    async with websockets.connect("ws://localhost:8080") as websocket:
        while True:
            message = await websocket.recv()
            packet = json.loads(message)
            telemetry_buffer.append(packet)


if __name__ == "__main__":
    try:
        asyncio.run(collect_data())
    except KeyboardInterrupt:
        print("\nTelemetry collector stopped")
