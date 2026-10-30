# Extracted from manuscript/book1-traditional/06-operating-systems.md §6.14.3 (listing 7). Edit the manuscript, not this file.
"""Atomically and durably replace a file on a POSIX system (Linux, macOS)."""
import os


def durable_replace(path: str, data: bytes) -> None:
    directory = os.path.dirname(os.path.abspath(path))
    tmp_path = path + ".tmp"

    fd = os.open(tmp_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o644)
    try:
        view = memoryview(data)
        while view:                          # write() may write fewer bytes than asked
            written = os.write(fd, view)
            view = view[written:]
        os.fsync(fd)                         # 1. file contents reach stable storage
    finally:
        os.close(fd)

    os.replace(tmp_path, path)               # 2. atomic rename over the old file

    dir_fd = os.open(directory, os.O_RDONLY)
    try:
        os.fsync(dir_fd)                     # 3. the rename itself (a directory entry) is durable
    finally:
        os.close(dir_fd)


if __name__ == "__main__":
    durable_replace("config.json", b'{"version": 2}\n')
    with open("config.json", "rb") as f:
        print(f.read())
