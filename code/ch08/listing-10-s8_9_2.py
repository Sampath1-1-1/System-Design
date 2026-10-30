# Extracted from manuscript/book1-traditional/08-web-application-fundamentals.md §8.9.2 (listing 10). Edit the manuscript, not this file.
def encode_varint(n: int) -> bytes:
    """Protocol Buffers base-128 varint for a non-negative integer."""
    out = bytearray()
    while True:
        byte = n & 0x7F               # take the low 7 bits
        n >>= 7
        if n:
            out.append(byte | 0x80)   # more bytes follow: set the MSB
        else:
            out.append(byte)          # last byte: MSB clear
            return bytes(out)


def encode_tag(field_number: int, wire_type: int) -> bytes:
    return encode_varint((field_number << 3) | wire_type)


def encode_string(field_number: int, s: str) -> bytes:
    data = s.encode("utf-8")
    return encode_tag(field_number, 2) + encode_varint(len(data)) + data


msg = (encode_string(1, "Martin")
       + encode_tag(2, 0) + encode_varint(1337)
       + encode_string(3, "daydreaming")
       + encode_string(3, "hacking"))
print(msg.hex(" "), len(msg), "bytes")
# 0a 06 4d 61 72 74 69 6e 10 b9 0a 1a 0b 64 61 79 64 72 65 61 6d 69 6e 67 1a 07 68 61 63 6b 69 6e 67 33 bytes
