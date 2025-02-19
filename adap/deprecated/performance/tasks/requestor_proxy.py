import sys
import urllib3
from adap.api_automation.utils.http_util import ApiResponse
from bs4 import BeautifulSoup
from adap.deprecated.performance.utils.locust_support import setup_wait_time
from locust import HttpLocust, TaskSet, seq_task
import os

urllib3.disable_warnings()

ENV = os.environ['TEST_ENV']
WAIT_CONFIG_TYPE = os.environ['WAIT_CONFIG_TYPE']
WAIT_TIME = os.environ['WAIT_TIME']
print(os.environ)
sys.path.append(os.getcwd())

email = ""
password = ""


class make(TaskSet):
    authenticity_token = ''

    def on_start(self):
        header = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache"
        }
        url = "/"
        with self.client.get(url, headers=header, catch_response=True) as response:
            if response.status_code != 200:
                response.failure("Incorrect response")
            else:
                api_response = ApiResponse(response)
                soup = BeautifulSoup(api_response.content, 'html.parser')
                value = soup.find('input', {'name': 'authenticity_token'}).get('value')
                self.authenticity_token = value
                print(self.authenticity_token)
                response.success()

        header = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "Content-Type": "application/x-www-form-urlencoded",
            "Connection": "keep-alive"
                }
        url = "sessions"
        payload = {"session[email]": email,
                   "session[password]": password,
                   "commit": "Sign In",
                   "authenticity_token": self.authenticity_token
                   }

        with self.client.post(url, data=payload, headers=header, catch_response=True) as response:
            if "<title>Figure Eight</title>" not in response.text:
                response.failure("Incorrect response")
            else:
                response.success()
                print(response.text)

    @seq_task(1)
    def requestorproxy(self):

        header = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache"
        }
        url = "https://requestor-proxy." + ENV + ".cf3.us/v1/me"
        with self.client.get(url, headers=header, catch_response=True) as response:
            if response.status_code != 200:
                response.failure("Incorrect response")
            else:
                response.success()


class WebsiteUser(HttpLocust):
    task_set = make
    host = "https://make." + ENV + ".cf3.us"

    def __init__(self):
        super(WebsiteUser, self).__init__()

    wait_time = setup_wait_time(WAIT_CONFIG_TYPE, WAIT_TIME)