# Extracted from manuscript/book1-traditional/09-real-time-communication.md §9.5.1 (listing 1). Edit the manuscript, not this file.
"""Minimal Server-Sent Events endpoint using only the standard library.

Run:   python3 sse_server.py
Test:  curl -N http://127.0.0.1:8080/events
       curl -N -H "Last-Event-ID: 3" http://127.0.0.1:8080/events
"""
import asyncio
import json
import time

HISTORY: list[tuple[int, str]] = []    # (event id, JSON payload) ring buffer
HISTORY_LIMIT = 1000
new_event = asyncio.Condition()

async def producer() -> None:
    """Pretend to be a business event source: one price tick per second."""
    event_id = 0
    while True:
        await asyncio.sleep(1)
        event_id += 1
        payload = json.dumps({"symbol": "ACME", "price": 100 + event_id, "ts": time.time()})
        async with new_event:
            HISTORY.append((event_id, payload))
            del HISTORY[:-HISTORY_LIMIT]          # keep the buffer bounded
            new_event.notify_all()

def format_event(event_id: int, data: str) -> bytes:
    return f"id: {event_id}\nevent: price\ndata: {data}\n\n".encode()

async def handle(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
    # 1. Read the request line and headers (no body for GET).
    request_line = await reader.readline()
    headers = {}
    while (line := await reader.readline()) not in (b"\r\n", b"\n", b""):
        name, _, value = line.decode().partition(":")
        headers[name.strip().lower()] = value.strip()
    if not request_line.startswith(b"GET /events"):
        writer.write(b"HTTP/1.1 404 Not Found\r\nContent-Length: 0\r\n\r\n")
        await writer.drain(); writer.close(); return

    # 2. Resume point: the browser sends Last-Event-ID automatically on reconnect.
    try:
        last_seen = int(headers.get("last-event-id", "0"))
    except ValueError:
        last_seen = 0

    writer.write(b"HTTP/1.1 200 OK\r\n"
                 b"Content-Type: text/event-stream\r\n"
                 b"Cache-Control: no-cache\r\n"
                 b"Connection: keep-alive\r\n\r\n"
                 b"retry: 5000\n\n")          # ask client to wait 5 s before reconnecting
    try:
        while True:
            # 3. Send everything newer than last_seen (replay, then live).
            pending = [(i, d) for i, d in HISTORY if i > last_seen]
            for event_id, data in pending:
                writer.write(format_event(event_id, data))
                last_seen = event_id
            if not pending:
                writer.write(b": keep-alive\n\n")   # comment line; defeats idle timeouts
            await writer.drain()                    # backpressure: wait if socket buffer full
            async with new_event:
                try:
                    await asyncio.wait_for(new_event.wait(), timeout=15)
                except asyncio.TimeoutError:
                    pass
    except (ConnectionResetError, BrokenPipeError):
        pass
    finally:
        writer.close()

async def main() -> None:
    asyncio.create_task(producer())
    server = await asyncio.start_server(handle, "127.0.0.1", 8080)
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())
