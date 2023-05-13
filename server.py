import random
from ctypes import c_uint
from socket import *

# TEA based on http://www.cs.sjsu.edu/~stamp/CS265/SecurityEngineering/chapter5_SE/tea
# FakeTLS based on https://medium.com/@raykaryshyn/an-implementation-of-faketls-85b94f496d72

ip = "localhost"
port = 2048 # change back to 443 after testing

K = [0x77652061, 0x72652072, 0x3373652d, 0x72636821] # TEA key
magic = 0x9e3779b9

def serverhello(connectionSocket):
    aa = bytes([0x16, 0x03, 0x03, 0x00, 0x7a, 0x02, 0x00, 0x00, 0x76, 0x03, 0x03])
    ab = random.randbytes(32)
    ac = bytes([0x20])
    ad = random.randbytes(32)
    ae = bytes([0x13, 0x02, 0x00, 0x00, 0x2e, 0x00, 0x2b, 0x00, 0x02, 0x03, 0x04, 0x00, 0x33, 0x00, 0x24, 0x00, 0x1d, 0x00, 0x20])
    af = random.randbytes(32)
    a = aa + ab + ac + ad + ae + af

    ba = bytes([0x17, 0x03, 0x03, 0x00, 0x17])
    bb = random.randbytes(23)
    b = ba + bb

    ca = bytes([0x17, 0x03, 0x03, 0x03, 0x43])
    cb = random.randbytes(835)
    c = ca + cb

    da = bytes([0x17, 0x03, 0x03, 0x01, 0x19])
    db = random.randbytes(281)
    d = da + db

    ea = bytes([0x17, 0x03, 0x03, 0x00, 0x45])
    eb = random.randbytes(69)
    e = ea + eb

    message = a + b + c + d + e
    connectionSocket.send(message)

def tobytes(ciphers: list[list[int]]) -> bytes:
    out = b''
    for x in range(0,9):
        out += ciphers[x][0].to_bytes(4, 'big') + ciphers[x][1].to_bytes(4, 'big')
    return out

def encrypt(command: list[int], previous: list[int]) -> bytes: # TEA encryption
    L = c_uint(command[0] ^ previous[0])
    R = c_uint(command[1] ^ previous[1])
    sum = c_uint()
    for x in range(0,32):
        sum.value += magic
        L.value += ((R.value << 4) + K[0]) ^ (R.value + sum.value) ^ ((R.value >> 5) + K[1])
        R.value += ((L.value << 4) + K[2]) ^ (L.value + sum.value) ^ ((L.value >> 5) + K[3])
    return [L.value, R.value]

def cbc(command: str) -> bytes:
    ciphers = [[random.randint(0,0xffffffff), random.randint(0, 0xffffffff)]] # iv
    for x in range(0,8):
        ciphers.append(encrypt([int.from_bytes(command[8*x:8*x+4].encode(), 'big'), int.from_bytes(command[8*x+4:8*x+8].encode(), 'big')], ciphers[x]))
    return tobytes(ciphers)

def main():
    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.bind((ip, port))
    serverSocket.listen(1)
    try:
        connectionSocket, clientAddress = serverSocket.accept()
    except:
        print("No connection")
    connectionSocket.recv(2048) # read client hello
    serverhello(connectionSocket)
    connectionSocket.recv(2048) # read client hello fin
    while True:
        command = input("Input command (type:parameter):")
        if len(command) > 64:
            print("Command exceeds length")
            continue
        padded = (command + ":").ljust(64, " ")
        ciphercmd = cbc(padded)
        connectionSocket.send(ciphercmd)

if __name__ == "__main__":
    main()
