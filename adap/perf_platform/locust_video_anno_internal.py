from adap.api_automation.services_config.video_annotation import Video_Annotation_Internal
from adap.api_automation.services_config.requestor_proxy import RP
from adap.data.units import hands_vid_annotation as hva
from adap.settings import Config
from utils.custom_locust import CustomLocust, event_monitor_users_count
from utils.logging import get_logger
from locust import TaskSet, task, between, events
import uuid
import json
import random

# stdout should be disabled inside locustfiles because locust already does that
log = get_logger(__name__, stdout=False)

events.master_start_hatching += event_monitor_users_count


class LocustUserBehavior(TaskSet):
    def on_start(self):
        self.api_service = Video_Annotation_Internal()
        self.requestor_proxy = RP(env=Config.ENV)

    def get_video_info(self):
        env_unit_ids = {
            'integration': '1bfbd1526274c7311d5cd92c49376fcd750e1ac9087b15f5a53439411caf9bd2',
            'qa': '77745d1f5b85ede62a770b0849f9b73747c9e2b6d8f690cf74a899d8b49ef0d9',
        }
        unit_id = env_unit_ids.get(Config.ENV)
        assert unit_id
        video_info_res = self.api_service.get_video_info(unit_id=unit_id)
        video_info_res.assert_response_status(200)
        assert video_info_res.json_response.get('frame_count'), "'frame_count' not found in response payload: " \
                                                                f"{video_info_res.json_response}"

    def post_annotation(self):
        annotations = [hva.frame_annotation for f in range(25)]
        annotationData = {
            'annotation': annotations,
            'job_id': 1000,
            'annotation_id': uuid.uuid4().__str__(),
        }
        save_anno_res = self.api_service.save_annotation(json.dumps(annotationData))
        save_anno_res.assert_response_status(200)
        assert save_anno_res.json_response.get('url'), "'url' not found in response payload: " \
                                                       f"{save_anno_res.json_response}"

    def post_object_tracking(self):
        env_unit_ids = {
            'integration': '022983c10ef5dea27543aac7b7be4e2b1869fca576564bbc93ff14efe8c5769e',
            'qa': 'eb594bee8e19ad33cc26d77fd9a99fc77df43eaf015e71e66482ae0840533aca',
        }
        video_id = env_unit_ids.get(Config.ENV)
        frame_id = random.choice(range(1, 236))
        data = {
            'video_id': video_id,
            'start_frame': frame_id,
            'tracked_frame_count': 10,
            'object_id': 1,
            'x': 1022,
            'y': 430,
            'width': 49,
            'height': 36
        }
        resp = self.api_service.object_tracking(json.dumps(data))
        resp.assert_response_status(200)

    def get_frame(self):
        env_unit_ids = {
            'integration': '022983c10ef5dea27543aac7b7be4e2b1869fca576564bbc93ff14efe8c5769e',
            'qa': 'eb594bee8e19ad33cc26d77fd9a99fc77df43eaf015e71e66482ae0840533aca',
        }
        video_id = env_unit_ids.get(Config.ENV)
        frame_id = random.choice(range(1, 246))
        resp = self.requestor_proxy.get_video_frame(
            video_id=video_id,
            frame_id=frame_id)
        assert resp.status_code == 200, resp.content

    @task()
    def caller(self):
        tasks_map = {
            'video_info': self.get_video_info,
            'save_annotation': self.post_annotation,
            'get_frame': self.get_frame,
            'object_tracking': self.post_object_tracking
        }
        if Config.LOCUST_TASK:
            task = tasks_map.get(Config.LOCUST_TASK)
            assert task is not None, "no matching function found for this LOCUST_TASK: " \
                                     f"{Config.LOCUST_TASK}"
        else:
            task = self.get_video_info

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
