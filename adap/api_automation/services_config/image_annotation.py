from adap.api_automation.services_config.endpoints import image_annotation_endpoints as eps
from adap.api_automation.utils.http_util import HttpMethod, ApiResponse
from adap.settings import Config


class Image_Annotation_Internal:
    """
    Internal API Endpoints
    """

    def __init__(self, **kwargs):
        env = kwargs.get('env') or Config.ENV
        self.base_url = f"https://image-annotation-service.internal.{env}.cf3.us"
        self.service = kwargs.get('service') or HttpMethod(session=False)
        pass

    def aggregate(self, data):
        url = self.base_url + eps.AGGREGATE
        resp = self.service.post(
            url,
            data=data,
            ep_name=eps.AGGREGATE)
        return resp

    def validate(self, data):
        url = self.base_url + eps.VALIDATE
        resp = self.service.post(
            url,
            data=data,
            ep_name=eps.VALIDATE)
        return resp

