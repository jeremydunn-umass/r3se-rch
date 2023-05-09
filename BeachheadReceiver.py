import socket

HOST = ''
PORT = 37123

def accept_connection():
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    sock.bind((HOST, PORT))
    sock.listen(1)

    conn, addr = sock.accept()

    data = b''
    while True:
        data_in = conn.recv(1024)
        data += data_in
        if len(data_in) < 1024:
            break
    sock.close()

    return data.decode('utf-8')

accept_connection()