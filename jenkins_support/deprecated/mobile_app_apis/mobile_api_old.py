# import json
# import allure
# import pytest
# from jenkins_support.deprecated.mobile_app_apis.mobile_api_endpoints import *
# from adap.api_automation.utils.http_util import HttpMethod
#
#
# class MOBILE_APIS:
#
#     def __init__(self, cookies=None, payload=None, custom_url=None, headers=None, env=None):
#         self.payload = payload
#         self.cookies = cookies
#
#         if env is None and custom_url is None:  env = pytest.env
#         self.env = env
#
#         if custom_url is not None:
#             self.url = custom_url
#         else:
#             self.url = URL(env=pytest.env)
#
#         if not headers:
#             self.headers = {
#                 'accept': 'application/json',
#                 'Content-Type': 'application/json'
#             }
#
#         self.service = HttpMethod(self.url, self.payload)
#
#     @allure.step
#     def get_third_party_signature(self, projectid=None, vendorid=None, payload=None, cookies=None):
#         if not cookies:
#             cookies = self.cookies
#         res = self.service.get(GET_THIRD_PARTY_SIGNATURE % (projectid, vendorid), headers=self.headers, cookies=cookies, params=payload)
#         return res
#
#     @allure.step
#     def post_third_party_signature(self, payload=None, cookies=None):
#         if not cookies:
#             cookies = self.cookies
#         res = self.service.post(POST_THIRD_PARTY_SIGNATURE, headers=self.headers, cookies=cookies,
#                                 data=json.dumps(payload), ep_name=POST_THIRD_PARTY_SIGNATURE)
#         return res
#
#     @allure.step
#     def post_document_signature(self, vendorid, payload=None, cookies=None):
#         if not cookies:
#             cookies = self.cookies
#         res = self.service.post(POST_DOCUMENT_SIGNATURE % vendorid, headers=self.headers, cookies=cookies,
#                                 data=json.dumps(payload), ep_name=POST_DOCUMENT_SIGNATURE)
#         return res
#
#     @allure.step
#     def get_user_service(self, vendorid=None, projectid=None, payload=None, cookies=None):
#         if not cookies:
#             cookies = self.cookies
#         res = self.service.get(GET_USER_SERVICE % (vendorid, projectid), headers=self.headers, cookies=cookies, params=payload)
#         return res
#
#     @allure.step
#     def get_all_projects(self, vendorid=None, payload=None, cookies=None):
#         if not cookies:
#             cookies = self.cookies
#         res = self.service.get(GET_ALL_PROJECTS % vendorid, headers=self.headers, cookies=cookies, params=payload)
#         return res
#
#     @allure.step
#     def post_apply_projects(self, payload=None, cookies=None):
#         if not cookies:
#             cookies = self.cookies
#         res = self.service.post(APPLY_PROJECTS, headers=self.headers, cookies=cookies,
#                                 data=json.dumps(payload), ep_name=APPLY_PROJECTS)
#         return res
#
#     @allure.step
#     def post_intelligent_attribute(self, vendorid, payload=None, cookies=None):
#         if not cookies:
#             cookies = self.cookies
#         res = self.service.post(POST_INTELLIGENT_ATTRIBUTE % vendorid, headers=self.headers, cookies=cookies,
#                                 data=json.dumps(payload), ep_name=POST_INTELLIGENT_ATTRIBUTE)
#         return res
#
#     @allure.step
#     def post_smart_phone(self, vendorid, payload=None, cookies=None):
#         if not cookies:
#             cookies = self.cookies
#         res = self.service.post(POST_SMART_PHONE % vendorid, headers=self.headers, cookies=cookies,
#                                 data=json.dumps(payload), ep_name=POST_SMART_PHONE)
#         return res