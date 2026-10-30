# Extracted from manuscript/book1-traditional/09-real-time-communication.md §9.6.3 (listing 3). Edit the manuscript, not this file.
import os
import struct

def encode_frame(payload: bytes, opcode: int = 0x1, mask: bool = True) -> bytes:
    """Build a single, unfragmented frame (FIN=1)."""
    first = 0x80 | opcode                      # FIN bit + opcode
    n = len(payload)
    mask_bit = 0x80 if mask else 0x00
    if n <= 125:
        header = struct.pack("!BB", first, mask_bit | n)
    elif n <= 0xFFFF:
        header = struct.pack("!BBH", first, mask_bit | 126, n)
    else:
        header = struct.pack("!BBQ", first, mask_bit | 127, n)
    if not mask:
        return header + payload
    key = os.urandom(4)                        # fresh masking key per frame
    masked = bytes(b ^ key[i % 4] for i, b in enumerate(payload))
    return header + key + masked

def decode_frame(frame: bytes):
    """Parse one complete frame; return (fin, opcode, payload)."""
    b0, b1 = frame[0], frame[1]
    fin, opcode = bool(b0 & 0x80), b0 & 0x0F
    masked, n = bool(b1 & 0x80), b1 & 0x7F
    pos = 2
    if n == 126:
        (n,) = struct.unpack("!H", frame[pos:pos + 2]); pos += 2
    elif n == 127:
        (n,) = struct.unpack("!Q", frame[pos:pos + 8]); pos += 8
    key = b""
    if masked:
        key = frame[pos:pos + 4]; pos += 4
    data = frame[pos:pos + n]
    if masked:
        data = bytes(b ^ key[i % 4] for i, b in enumerate(data))
    return fin, opcode, data

print(encode_frame(b"Hello", mask=False).hex(" "))  # 81 05 48 65 6c 6c 6f
f = encode_frame(b"Hello")                           # 11 bytes: 2 header + 4 key + 5
print(len(f), decode_frame(f))                       # 11 (True, 1, b'Hello')
