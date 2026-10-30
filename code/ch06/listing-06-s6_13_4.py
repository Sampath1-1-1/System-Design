# Extracted from manuscript/book1-traditional/06-operating-systems.md §6.13.4 (listing 6). Edit the manuscript, not this file.
"""A single-threaded echo server: one event loop, many connections.

On Linux, selectors.DefaultSelector is backed by epoll; on macOS/BSD by kqueue.
"""
import selectors
import socket

sel = selectors.DefaultSelector()


def accept(server: socket.socket) -> None:
    conn, _addr = server.accept()              # ready, so this will not block
    conn.setblocking(False)
    sel.register(conn, selectors.EVENT_READ, handle)


def handle(conn: socket.socket) -> None:
    data = conn.recv(4096)                     # ready, so this will not block
    if data:
        conn.sendall(data)                     # simplification: assumes the send buffer has room
    else:                                      # empty read = peer closed
        sel.unregister(conn)
        conn.close()


def serve(host: str = "127.0.0.1", port: int = 9000) -> None:
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    server.listen(1024)
    server.setblocking(False)
    sel.register(server, selectors.EVENT_READ, accept)
    print(f"selector = {type(sel).__name__}; listening on {host}:{port}")
    while True:                                # THE event loop
        for key, _mask in sel.select():        # block until >= 1 socket is ready
            callback = key.data
            callback(key.fileobj)              # run the handler; it must not block


if __name__ == "__main__":
    serve()
