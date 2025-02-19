from locust import HttpLocust, TaskSet, task, seq_task
import os
from adap.deprecated.performance.utils.locust_support import setup_wait_time

ENV = os.environ['TEST_ENV']
WAIT_CONFIG_TYPE = os.environ['WAIT_CONFIG_TYPE']
WAIT_TIME = os.environ['WAIT_TIME']



class imageAnnotation(TaskSet):

    @task
    @seq_task(1)
    def validate_box(self):
        validate_payload = {
            "similarity_thresholds": {"box": 0.6, "dot": 10, "line": 2, "polygon": 0.6},
            "confidence_thresholds": {"box": 0.6, "dot": 0.8, "line": 0.8, "polygon": 0.6, "class": 0.5},
            "test_annotations": [
                {
                    "id": "123",
                    "class": "car",
                    "type": "box",
                    "coordinates": {"x": 50, "y": 437, "h": 86, "w": 59}
                }
            ],
            "annotations": [
                {
                    "id": "001",
                    "class": "car",
                    "type": "box",
                    "coordinates": {"x": 50, "y": 437, "h": 86, "w": 59}
                }
            ]
        }

        header = {
            "Content-Type": "application/json",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache"
        }
        url = "/api/v1/validate"

        with self.client.post(url, json=validate_payload, headers=header, catch_response=True) as response:
            if "annotations" not in response.text:
                response.failure("Incorrect response")
            else:
                response.success()


class WebsiteUser(HttpLocust):
    task_set = imageAnnotation
    host = "https://image-annotation-service.internal." + ENV + ".cf3.us"

    def __init__(self):
        super(WebsiteUser, self).__init__()

    wait_time = setup_wait_time(WAIT_CONFIG_TYPE, WAIT_TIME)