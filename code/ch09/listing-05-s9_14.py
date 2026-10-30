# Extracted from manuscript/book1-traditional/09-real-time-communication.md §9.14 (listing 5). Edit the manuscript, not this file.
"""Room-based WebSocket chat server with heartbeats and slow-consumer protection."""
import asyncio
import json

from websockets.asyncio.server import serve, ServerConnection
from websockets.exceptions import ConnectionClosed

OUTBOX_LIMIT = 100                         # max queued messages per client
rooms: dict[str, set["Client"]] = {}

class Client:
    def __init__(self, ws: ServerConnection, room: str, name: str):
        self.ws, self.room, self.name = ws, room, name
        self.outbox: asyncio.Queue[str] = asyncio.Queue(maxsize=OUTBOX_LIMIT)

    def offer(self, message: str) -> None:
        """Non-blocking enqueue; a full outbox means a slow consumer."""
        try:
            self.outbox.put_nowait(message)
        except asyncio.QueueFull:
            # Policy: disconnect slow consumers rather than buffer without limit.
            asyncio.ensure_future(self.ws.close(code=1008, reason="slow consumer"))

    async def writer(self) -> None:
        while True:
            message = await self.outbox.get()
            await self.ws.send(message)    # awaits if the TCP send buffer is full

def publish(room: str, sender: str, text: str) -> None:
    message = json.dumps({"room": room, "from": sender, "text": text})
    for client in list(rooms.get(room, ())):
        client.offer(message)

async def handler(ws: ServerConnection) -> None:
    # First message must be a join: {"room": "...", "name": "..."}
    try:
        hello = json.loads(await asyncio.wait_for(ws.recv(), timeout=10))
        room, name = str(hello["room"]), str(hello["name"])
    except (asyncio.TimeoutError, ValueError, KeyError, TypeError):
        await ws.close(code=1008, reason="expected join message")
        return

    client = Client(ws, room, name)
    rooms.setdefault(room, set()).add(client)
    writer_task = asyncio.create_task(client.writer())
    publish(room, "system", f"{name} joined")
    try:
        async for raw in ws:                       # reader loop
            if isinstance(raw, str) and len(raw) <= 4096:
                publish(room, name, raw)
    except ConnectionClosed:
        pass
    finally:
        writer_task.cancel()
        rooms[room].discard(client)
        if not rooms[room]:
            del rooms[room]
        publish(room, "system", f"{name} left")

async def main() -> None:
    # Ping every 20 s; close if no Pong within 20 s (detects dead TCP peers).
    async with serve(handler, "127.0.0.1", 8765,
                     ping_interval=20, ping_timeout=20,
                     max_size=64 * 1024) as server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())
