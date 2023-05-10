# echo-client.py

import socket

HOST = "10.0.2.45"  # The server's hostname or IP address
PORT = 37123  # The port used by the server

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(b"Hello, world")
