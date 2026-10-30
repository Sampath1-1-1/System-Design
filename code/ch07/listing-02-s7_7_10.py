# Extracted from manuscript/book1-traditional/07-networking-fundamentals.md §7.7.10 (listing 2). Edit the manuscript, not this file.
# echo_client.py — measures connect time and one request/response round trip.
import socket, time

t0 = time.perf_counter()
s = socket.create_connection(("127.0.0.1", 9000))   # SYN, SYN-ACK, ACK
t1 = time.perf_counter()
s.sendall(b"hello")
reply = s.recv(4096)
t2 = time.perf_counter()
s.close()                                             # client is active closer: TIME_WAIT here
print(reply, f"connect={1e3*(t1-t0):.3f} ms  rtt={1e3*(t2-t1):.3f} ms")
