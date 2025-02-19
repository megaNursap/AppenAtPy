
from adap.api_automation.services_config.endpoints import video_annotation_endpoints as eps
from adap.api_automation.utils.http_util import HttpMethod
from adap.settings import Config
import pytest

class Video_Annotation_Internal:
    """
    Internal API Endpoints
    """

    def __init__(self, **kwargs):
        self.env = kwargs.get('env') or Config.ENV
        self.service = kwargs.get('service') or HttpMethod(session=False)
        if self.env == 'fed':
            if pytest.customize_fed == 'true':
                self.service.base_url = eps.FED_CUSTOMIZE.format(pytest.customize_fed_url)
            else:
                self.service.base_url = eps.FED.format(pytest.env_fed)
        else:
            self.service.base_url = eps.URL.format(env=self.env)

    def get_video_info(self, unit_id):
        resp = self.service.get(
            eps.VIDEO_INFO,
            params={'row_id': unit_id},
            ep_name=eps.VIDEO_INFO)
        return resp

    def save_annotation(self, data):
        resp = self.service.post(
            eps.ANNOTATION,
            data=data,
            ep_name=eps.ANNOTATION)
        return resp

    def object_tracking(self, data):
        resp = self.service.post(
            eps.OBJECT_TRACKING,
            data=data,
            ep_name=eps.OBJECT_TRACKING)
        return resp

    def get_frame(self, video_id: str, frame_id: int):
        ep = eps.FRAME.format(
            video_id=video_id,
            frame_id=frame_id
            )
        resp = self.service.get(
            ep,
            ep_name='video_frame_jpg')
        return resp

    def test(self):
        # eps.TEST
        # TODO
        pass
