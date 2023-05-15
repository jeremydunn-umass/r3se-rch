
import socket

HOST=''
PORT = 37123  


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.bind((HOST, PORT))
    sock.listen(1)
    conn, addr = sock.accept()

    data = b""
    while True:
        data_in = conn.recv(1024)
        data += data_in
        if len(data_in) < 1024:
            break

    sock.sendall(data)

