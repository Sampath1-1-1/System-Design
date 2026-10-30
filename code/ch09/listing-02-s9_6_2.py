# Extracted from manuscript/book1-traditional/09-real-time-communication.md §9.6.2 (listing 2). Edit the manuscript, not this file.
import base64
import hashlib

GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"  # fixed by RFC 6455

def accept_key(sec_websocket_key: str) -> str:
    """Compute Sec-WebSocket-Accept from the client's Sec-WebSocket-Key."""
    digest = hashlib.sha1((sec_websocket_key + GUID).encode("ascii")).digest()
    return base64.b64encode(digest).decode("ascii")

print(accept_key("dGhlIHNhbXBsZSBub25jZQ=="))   # s3pPLMBiTxaQ9kYGzzhZRbK+xOo=
