# Extracted from manuscript/book1-traditional/13-storage-engine-internals.md §13.3.2 (listing 1). Edit the manuscript, not this file.
"""A minimal slotted page: header, slot array growing forward, records growing
backward from the end of the page. Record IDs (slot numbers) never change."""
import struct

PAGE_SIZE = 4096
HEADER = struct.Struct("<HH")      # slot_count, free_end (offset where record space begins)
SLOT = struct.Struct("<HH")        # record offset, record length (offset 0 = deleted slot)


class SlottedPage:
    def __init__(self):
        self.buf = bytearray(PAGE_SIZE)
        HEADER.pack_into(self.buf, 0, 0, PAGE_SIZE)

    def _header(self):
        return HEADER.unpack_from(self.buf, 0)

    def _slot_pos(self, slot):
        return HEADER.size + slot * SLOT.size

    def free_space(self):
        count, free_end = self._header()
        return free_end - (HEADER.size + count * SLOT.size)

    def insert(self, record: bytes) -> int:
        count, free_end = self._header()
        if len(record) + SLOT.size > self.free_space():
            self.compact()                                   # reclaim holes, then retry
            count, free_end = self._header()
            if len(record) + SLOT.size > self.free_space():
                raise ValueError("page full")
        offset = free_end - len(record)
        self.buf[offset:free_end] = record                   # record grows downward
        SLOT.pack_into(self.buf, self._slot_pos(count), offset, len(record))
        HEADER.pack_into(self.buf, 0, count + 1, offset)     # slot array grows upward
        return count                                         # slot number = stable record ID

    def get(self, slot: int) -> bytes:
        offset, length = SLOT.unpack_from(self.buf, self._slot_pos(slot))
        if offset == 0:
            raise KeyError(f"slot {slot} deleted")
        return bytes(self.buf[offset:offset + length])

    def delete(self, slot: int) -> None:
        SLOT.pack_into(self.buf, self._slot_pos(slot), 0, 0) # leaves a hole until compact()

    def compact(self) -> None:
        """Slide live records to the end of the page; slot numbers stay the same."""
        count, _ = self._header()
        live = []
        for s in range(count):
            off, length = SLOT.unpack_from(self.buf, self._slot_pos(s))
            if off:
                live.append((s, bytes(self.buf[off:off + length])))
        free_end = PAGE_SIZE
        for s, rec in live:
            free_end -= len(rec)
            self.buf[free_end:free_end + len(rec)] = rec
            SLOT.pack_into(self.buf, self._slot_pos(s), free_end, len(rec))
        HEADER.pack_into(self.buf, 0, count, free_end)


if __name__ == "__main__":
    page = SlottedPage()
    ids = [page.insert(b"row-%03d:" % i + b"x" * 90) for i in range(39)]
    print("inserted", len(ids), "records; free bytes:", page.free_space())
    for s in ids[::2]:
        page.delete(s)                                       # punch 20 holes
    print("after deleting 20, free bytes before compaction:", page.free_space())
    new = page.insert(b"a-larger-record:" + b"y" * 400)      # forces compaction
    print("new record got slot", new, "; slot 1 still reads", page.get(1)[:8])
    print("free bytes now:", page.free_space())
