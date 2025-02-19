import json
from adap.deprecated.performance.utils.locust_support import setup_wait_time
from locust import HttpLocust, TaskSet, task, seq_task
import os
import sys

ENV = os.environ['TEST_ENV']
WAIT_CONFIG_TYPE = os.environ['WAIT_CONFIG_TYPE']
WAIT_TIME = os.environ['WAIT_TIME']
sys.path.append(os.getcwd())

payload_get_annotation = {
    "job_id": 11000
    }

payload_post_annotation = {"id": "123abc45de6faaa",
                           "job_id": 10000,
                           "payload": {
                               "key_1": "value_1",
                               "key_2": "value_2"
                           }
                           }

payload_get_aggregation = {
  "unit_id": 99999,
  "data": {
    "text": "The subsidized wireless service should be available on Surge Volt Android devices with Moolah install kits, as well as on SIM Starter Kits distributed by Surge. Moolah and Surge said they will roll this out Florida, Virginia, Georgia and Texas initially, with an aim of reaching 40,000 locations by the end of the year."
  },
  "judgments_count": 3,
  "judgments": [
    {
      "id": 45155145,
      "trust": 0.86,
      "data": {
        "job_id": 11000,
        "annotation_id": "abc11000c1"
      }
    },
    {
      "id": 45155145,
      "trust": 0.86,
      "data": {
        "job_id": 11000,
        "annotation_id": "abc11000c2"
      }
    },
    {
      "id": 45155145,
      "trust": 0.83,
      "data": {
        "job_id": 11000,
        "annotation_id": "abc11000c3"
      }
    }
  ],
  "confidence_threshold": 0
}
payload_post_accuracy = {
    "unit_id": 99999,
    "judgments": [
        {
            "id": 45155145,
            "trust": 0.86,
            "data": {
                "job_id": 11000,
                "annotation_id": "abc11000c1"
            }
        },
        {
            "id": 45155145,
            "trust": 0.86,
            "data": {
                "job_id": 11000,
                "annotation_id": "abc11000c2"
            }
        },
        {
            "id": 45155145,
            "trust": 0.83,
            "data": {
                "job_id": 11000,
                "annotation_id": "abc11000c3"
            }
        }
    ],
    "correct_response": {
        "job_id": 11000,
        "annotation_id": "abc11000"
    }
}

payload_post_grade = {
    "contributor_response": {
        "job_id": 11000,
        "annotation_id": "abc11000c3"
    },
    "correct_response": {
        "job_id": 11000,
        "annotation_id": "abc11000"
    }
}
payload_put_grade = {
    "job_id": 11000,
    "annotation_id": "abc11000c1"
}


class text_annotation(TaskSet):

    @task
    @seq_task(1)
    def post_annotation(self):
        annotation = None
        header = {
            "Content-Type": "application/json",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache"
        }
        url = "/annotations"

        with self.client.post(url, headers=header, data=json.dumps(payload_post_annotation),
                              catch_response=True) as response:
            if response.status_code != 200 and "annotation_id\":\"" in response.text:
                response.failure("Incorrect response")
            else:
                response.success()
                annotation = response.json()['annotation_id']

    @task
    @seq_task(2)
    def get_annotation(self):
        header = {
            "Content-Type": "application/json",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache"
        }
        url = "/annotations/123abc45de6faaa"

        with self.client.get(url, headers=header, data=json.dumps(payload_get_annotation),
                             catch_response=True) as response:
            if response.status_code != 200 and "url" in response.text:
                response.failure("Incorrect response")
            else:
                response.success()

    @task
    @seq_task(3)
    def post_accuracy(self):
        header = {
            "Content-Type": "application/json",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache"
        }
        url = "/accuracy_details"

        with self.client.post(url, headers=header, data=json.dumps(payload_post_accuracy),
                              catch_response=True) as response:
            if response.status_code != 200 and "accuracy_details_url" in response.text:
                response.failure("Incorrect response")
            else:
                response.success()

    @task
    @seq_task(4)
    def get_aggregation(self):
        header = {
            "Content-Type": "application/json",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache"
        }
        url = "/aggregations/agg"

        with self.client.post(url, headers=header, data=json.dumps(payload_get_aggregation),
                              catch_response=True) as response:
            if response.status_code != 200 and "agg_report_url" in response.text:
                response.failure("Incorrect response")
            else:
                response.success()

    @task
    @seq_task(5)
    def post_grade(self):
        header = {
            "Content-Type": "application/json",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache"
        }
        url = "/grade"

        with self.client.post(url, headers=header, data=json.dumps(payload_post_grade),
                              catch_response=True) as response:
            if response.status_code != 200 and "{\"status\":\"" in response.text:
                response.failure("Incorrect response")
            else:
                response.success()

    @task
    @seq_task(6)
    def put_grade(self):
        header = {
            "Content-Type": "application/json",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache"
        }
        url = "/grade"

        with self.client.put(url, headers=header, data=json.dumps(payload_put_grade),
                             catch_response=True) as response:
            if response.status_code != 200 and "url" in response.text:
                response.failure("Incorrect response")
            else:
                response.success()


class WebsiteUser(HttpLocust):
    task_set = text_annotation
    host = "https://text-annotation.internal." + ENV + ".cf3.us"

    def __init__(self):
        super(WebsiteUser, self).__init__()

    wait_time = setup_wait_time(WAIT_CONFIG_TYPE, WAIT_TIME)
