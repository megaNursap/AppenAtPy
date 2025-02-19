"""
HTTP Client based on geventhttpclient, faster than request
"""


import socket
socket.setdefaulttimeout(60)

from adap.perf_platform.utils.results_handler import timeit
from geventhttpclient import HTTPClient as OG_HTTPClient
from geventhttpclient.url import URL
from geventhttpclient.response import HTTPSocketPoolResponse
import json


class Response:
    def __init__(self, response: HTTPSocketPoolResponse):
        self.status_code = response.status_code
        self.status_message = response.status_message
        self.json_response = {}
        if resp_body:= response.read().decode('utf8'):
            self.body = resp_body
            try:
                self.json_response = json.loads(resp_body)
            except Exception:
                pass

class HTTPClient:
    def __init__(self, base_url, concurrency=10):
        self.url = URL(base_url)
        self.http = OG_HTTPClient.from_url(
            self.url,
            concurrency=concurrency,
            connection_timeout=60,
            network_timeout=60)
    
    @timeit
    def get(self, url, headers=None, ep_name=''):
        url = URL(url)
        response = Response(
            self.http.get(
                url.request_uri,
                headers=headers
            )
        )

        return response

    @timeit
    def post(self, url, headers=None, data=None, ep_name=''):
        url = URL(url)
        response = Response(
            self.http.post(
                url.request_uri,
                body=data,
                headers=headers
            )
        )
        return response
