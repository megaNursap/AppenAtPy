from adap.api_automation.services_config.image_annotation import Image_Annotation_Internal
from adap.data.image_annotation import internal_service_data as data
from adap.settings import Config
from utils.custom_locust import CustomLocust, event_monitor_users_count
from utils.logging import get_logger
from locust import TaskSet, task, between, events
import json

log = get_logger(__name__, stdout=False)

events.master_start_hatching += event_monitor_users_count


class LocustUserBehavior(TaskSet):
    def on_start(self):
        self.api_service = Image_Annotation_Internal()

    def aggregate(self):
        request_body = data.aggregate
        aggregate_res = self.api_service.aggregate(json.dumps(request_body))
        aggregate_res.assert_response_status(200)

    def validate(self):
        request_body = data.validate
        validate_res = self.api_service.validate(json.dumps(request_body))
        validate_res.assert_response_status(200)
        assert validate_res.json_response.get('annotations'), "'annotations' not found in response payload: " \
                                                           f"{validate_res.json_response}"
        assert validate_res.json_response.get('grades'), "'grades' not found in response payload: " \
                                                           f"{validate_res.json_response}"
        assert validate_res.json_response.get('scores'), "'scores' not found in response payload: " \
                                                           f"{validate_res.json_response}"
        assert validate_res.json_response.get('status'), "'status' not found in response payload: " \
                                                           f"{validate_res.json_response}"

    @task()
    def caller(self):
        tasks_map = {
            'aggregate': self.aggregate,
            'validate': self.validate,
        }
        task = tasks_map.get(Config.LOCUST_TASK)
        assert task is not None, "no matching function found for this LOCUST_TASK: " \
                                     f"{Config.LOCUST_TASK}"

        self.client.locust_event(
            "Request",  # Requst type
            task.__name__,  # Requst name
            task,
            )


class LocustUser(CustomLocust):
    wait_time = between(0.1, 0.2)  # wait time between tasks, in seconds
    task_set = LocustUserBehavior

    def __init__(self):
        self.host = ''
        super(LocustUser, self).__init__()
