# Extracted from manuscript/book1-traditional/07-networking-fundamentals.md §7.7.10 (listing 1). Edit the manuscript, not this file.
# echo_server.py — a minimal, runnable TCP echo server (Python 3.8+).
import socket

HOST, PORT = "127.0.0.1", 9000

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # rebind despite TIME_WAIT
    srv.bind((HOST, PORT))
    srv.listen(128)                         # backlog of completed handshakes
    print(f"listening on {HOST}:{PORT}")
    while True:
        conn, addr = srv.accept()           # handshake already done by the kernel
        with conn:
            conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            while True:
                data = conn.recv(4096)      # may return fewer bytes than were sent
                if not data:                # empty read: peer sent FIN
                    break
                conn.sendall(data)          # loops until every byte is queued
