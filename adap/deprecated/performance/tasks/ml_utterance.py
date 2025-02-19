import sys
from locust import HttpLocust, TaskSet, task, seq_task
import os
from adap.deprecated.performance.utils.locust_support import setup_wait_time


ENV = os.environ['TEST_ENV']
WAIT_CONFIG_TYPE = os.environ['WAIT_CONFIG_TYPE']
WAIT_TIME = os.environ['WAIT_TIME']
sys.path.append(os.getcwd())


class ml_utterance(TaskSet):

    @task
    @seq_task(1)
    def coherence_detection(self):
        header = {
            "Content-Type": "application/json",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache"
        }
        url = "base_models/f8-coherence-detection/predict"
        payload = {
            "text": "The quick brown fox jumps over the lazy dog."
        }
        with self.client.post(url, json=payload, headers=header, catch_response=True) as response:
            if "coherence_confidence" not in response.text:
                response.failure("Incorrect response")
            else:
                response.success()

    @task
    @seq_task(2)
    def language_detection(self):
        header = {
            "Content-Type": "application/json",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache"
        }
        url = "base_models/f8-language-detection/predict"
        payload2 = {
            "text": "The quick brown fox jumps over the lazy dog."
        }
        with self.client.post(url, json=payload2, headers=header, catch_response=True) as response:
            if "lang_confidence" not in response.text:
                response.failure("Incorrect response")
            else:
                response.success()


class WebsiteUser(HttpLocust):
    task_set = ml_utterance
    host = "https://ml-api.internal."+ENV +".cf3.us"

    def __init__(self):
        super(WebsiteUser, self).__init__()

    wait_time = setup_wait_time(WAIT_CONFIG_TYPE, WAIT_TIME)
