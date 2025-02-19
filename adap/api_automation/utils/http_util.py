from adap.perf_platform.utils.results_handler import timeit
from adap.settings import Config
import requests
import json
import allure
import logging
import warnings

warnings.filterwarnings("ignore")

LOGGER = logging.getLogger(__name__)
if not Config.LOG_HTTP:
    LOGGER.disabled = True


class ApiHeaders:
    @staticmethod
    def get_default_headers():
        get_headers = {
            "Accept": "application/json"
        }
        return get_headers

    @staticmethod
    def post_default_headers():
        post_headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        return post_headers

    @staticmethod
    def post_default_csv_headers():
        post_headers = {
            "Content-Type": "text/csv"
        }
        return post_headers

    @staticmethod
    def get_zip_headers():
        get_headers = {
            "Content-Type": "application/zip",
            "Accept-Encoding": "gzip, deflate"
        }
        return get_headers


class ApiResponse:

    def __init__(self, response):
        self._response = response
        self.status_code = response.status_code
        self.content = response.content
        self.text = response.text
        self.cookies = response.cookies
        self.headers = response.headers
        self.url = response.url
        self.history = response.history
        try:
            self.json_response = response.json()
        except ValueError:
            self.json_response = {}

        # LOGGER.debug(HttpMethod.get_curl(response.request))

    def __repr__(self):
        return '{} (status_code={!r}, contents=..., cookies=..., json_response=...)'.format(
            type(self).__name__, self.status_code)

    def assert_response_status(self, status):
        assert status == self.status_code, "Expected status: %s \n Actual status: %s" % (status, self.status_code)

    def assert_job_title(self, title):
        assert title == self.json_response['title'], "Expected title: %s \n Actual title: %s" % (
            title, self.json_response['title'])

    def assert_job_message(self, message):
        assert self.json_response['message'] == message

    def assert_request_response(self, resp):
        assert self.json_response == resp

    def assert_success_message(self, success, data=None):
        assert self.json_response['success'] == success % data

    def assert_success_message_no_data(self, message):
        assert self.json_response['success'] == message

    def assert_success_message_v2(self, message):
        assert self.json_response['success']['message'] == message

    def assert_error_message(self, message):
        assert self.json_response['error']['message'] == message

    def assert_error_message_v2(self, message):
        assert self.json_response['error'] == message


class HttpMethod:
    def __init__(self, base_url='', payload=None, session=None):
        self.base_url = base_url
        self.payload = payload
        if session:
            self.request = requests.Session()
        else:
            self.request = requests

    def endpoint(self, path):
        return self.base_url + path

    @timeit
    @allure.step
    def get(self, endpoint, headers=None, params=None, ep_name='', **kwargs):
        if headers is None:
            headers = ApiHeaders().post_default_headers()
        endpoint = self.endpoint(endpoint)

        LOGGER.info(f"""Sending GET API request
                        Endpoint: %s
                        Headers: %s params %s""" % (endpoint, headers, params))

        res = self.request.get(endpoint, headers=headers, params=params, verify=False, **kwargs)

        LOGGER.info("Response Code: %s" % res.status_code)
        LOGGER.debug(f"Response Content: %s" % res.content)

        api_response = ApiResponse(res)

        LOGGER.debug(f"Response Payload: %s" % api_response.json_response)

        return api_response

    @timeit
    @allure.step
    def get_report(self, endpoint, params=None, ep_name='', **kwargs):
        endpoint = self.endpoint(endpoint)

        LOGGER.info(f"""Sending GET API request
                           Endpoint: %s""" % endpoint)

        res = self.request.get(endpoint, params=params, verify=False, **kwargs)

        LOGGER.info("Response Code: %s" % res.status_code)
        LOGGER.debug(f"Response Content: %s" % res.content)

        return res

    @timeit
    @allure.step
    def post(self, endpoint, headers=None, data=None, ep_name='', verify=False, **kwargs):

        if headers is None:
            headers = ApiHeaders().post_default_headers()

        if data is None:
            data = json.dumps(self.payload)

        endpoint = self.endpoint(endpoint)
        LOGGER.info(f"""Sending POST API request
                        Endpoint: %s
                        Headers: %s
                        Request Payload: %s""" % (endpoint, headers, data))

        res = self.request.post(endpoint, data=data, headers=headers, verify=verify, **kwargs)
        LOGGER.info("Response Code: %s" % res.status_code)

        api_response = ApiResponse(res)
        LOGGER.info(f"Response Payload: %s" % api_response.json_response)

        return api_response

    @timeit
    @allure.step
    def delete(self, endpoint, headers=None, ep_name='', **kwargs):
        if headers is None:
            headers = ApiHeaders().post_default_headers()
        endpoint = self.endpoint(endpoint)

        LOGGER.info(f"""Sending DELETE API request
                        Endpoint: %s
                        Headers: %s""" % (endpoint, headers))

        res = self.request.delete(endpoint, headers=headers, verify=False, **kwargs)
        LOGGER.info("Response Code: %s" % res.status_code)
        LOGGER.debug(f"Response Content: %s" % res.content)
        return ApiResponse(res)

    @timeit
    @allure.step
    def put(self, endpoint, data=None, headers=None, params=None, ep_name='', **kwargs):

        if headers is None:
            headers = ApiHeaders().post_default_headers()

        if data is None:
            data = json.dumps(self.payload)

        endpoint = self.endpoint(endpoint)

        LOGGER.info(f"""Sending PUT API request
                        Endpoint: %s
                        Headers: %s
                        Request Payload: %s""" % (endpoint, headers, data))

        res = self.request.put(endpoint, data=data, headers=headers, params=params, verify=False, **kwargs)
        LOGGER.info("Response Code: %s" % res.status_code)

        api_response = ApiResponse(res)
        LOGGER.debug(f"Response Payload: %s" % api_response.json_response)

        return api_response

    @timeit
    @allure.step
    def patch(self, endpoint, data=None, headers=None, params=None, ep_name='', **kwargs):

        if headers is None:
            headers = ApiHeaders().post_default_headers()

        if data is None:
            data = json.dumps(self.payload)

        endpoint = self.endpoint(endpoint)

        LOGGER.info(f"""Sending PATCH API request
                           Endpoint: %s
                           Headers: %s
                           Request Payload: %s""" % (endpoint, headers, self.payload))

        res = self.request.patch(endpoint, data=data, headers=headers, params=params, verify=False, **kwargs)
        LOGGER.info("Response Code: %s" % res.status_code)

        api_response = ApiResponse(res)
        LOGGER.debug(f"Response Payload: %s" % api_response.json_response)

        return api_response

    @staticmethod
    def get_curl(req):
        command = "curl -X {method} -H {headers} -d '{data}' '{uri}'"
        method = req.method
        uri = req.url
        data = req.body
        headers = ['"{0}: {1}"'.format(k, v) for k, v in req.headers.items()]
        headers = " -H ".join(headers)

        return command.format(method=method, headers=headers, data=data, uri=uri)
