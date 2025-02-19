import json

import allure
import pytest

from adap.api_automation.utils.http_util import HttpMethod
from appen_connect.api_automation.services_config.endpoints.file_upload import *


class FileUploadAPI:
    def __init__(self, cookies=None, payload=None, custom_url=None, headers=None, env=None):
        self.payload = payload
        self.cookies = cookies

        if env is None and custom_url is None:  env = pytest.env
        self.env = env

        if custom_url is not None:
            self.url = custom_url
        else:
            self.url = URL(env=pytest.env)

        if not headers:
            self.headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Cache-Control": "no-cache"
            }
        self.service = HttpMethod(self.url, self.payload)

    @allure.step
    def get_presigned_url(self,  client_id=0, upload_type=None,file_name=None, cookies=None):
        if not cookies:
            cookies = self.cookies
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }
        res = self.service.get(GET_PRE_SIGNED_URL_BY_UPLOAD_TYPE.format(dataUploadType=upload_type, clientId=client_id, headers=self.headers, fileName=file_name), cookies=cookies,
                               ep_name=GET_PRE_SIGNED_URL_BY_UPLOAD_TYPE)
        return res

    @allure.step
    def upload_file(self,  payload=None, cookies=None):
        if not cookies:
            cookies = self.cookies
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }
        res = self.service.post(UPLOAD_DATA_FILE, headers=headers, cookies=cookies, data=json.dumps(payload),
                                ep_name=UPLOAD_DATA_FILE)
        return res

    @allure.step
    def get_uploaded_file_by_id(self, fileId=None, cookies=None):
        if not cookies:
            cookies = self.cookies
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }
        res = self.service.get(GET_UPLOADED_FILE_BY_ID.format( headers=headers,fileId=fileId), cookies=cookies,
                                ep_name=GET_UPLOADED_FILE_BY_ID)
        return res

    @allure.step
    def get_column_mapping_client_id(self,clientId=0, type=None, cookies=None):
        if not cookies:
            cookies = self.cookies
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }

        res = self.service.get(GET_PARTNER_DATA_COLUMN_MAPPING.format(clientId=clientId)+"?type={}".format(type),cookies=cookies, headers=headers,
                               ep_name=GET_PARTNER_DATA_COLUMN_MAPPING)
        return res

    @allure.step
    def check_template_exists(self, template_name=None, cookies=None):
        if not cookies:
            cookies = self.cookies
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }

        res = self.service.get(CHECK_TEMPLATE_EXISTS.format(template_name=template_name),cookies=cookies, headers=headers,
                               ep_name=CHECK_TEMPLATE_EXISTS)
        return res

    @allure.step
    def get_column_headers(self, file_id=None, cookies=None):
        if not cookies:
            cookies = self.cookies
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }

        res = self.service.get(GET_PARTNER_DATA_COLUMN_MAPPING_HEADERS.format(fileId=file_id),cookies=cookies, headers=headers,
                               ep_name=GET_PARTNER_DATA_COLUMN_MAPPING_HEADERS)
        return res

    @allure.step
    def get_column_types(self,  cookies=None):
        if not cookies:
            cookies = self.cookies
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }

        res = self.service.get(GET_PARTNER_DATA_COLUMN_TYPES_DICTIONARY, cookies=cookies, headers=headers,
                               ep_name=GET_PARTNER_DATA_COLUMN_TYPES_DICTIONARY)
        return res

    @allure.step
    def create_column_mapping(self, payload=None, cookies=None):
        if not cookies:
            cookies = self.cookies
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }
        res = self.service.post(PARTNER_DATA_COLUMN_MAPPING, headers=headers, cookies=cookies, data=json.dumps(payload),
                                ep_name=PARTNER_DATA_COLUMN_MAPPING)
        return res

    @allure.step
    def get_columns(self, column_mapping_id=None, cookies=None):
        if not cookies:
            cookies = self.cookies
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }

        res = self.service.get(GET_PARTNER_DATA_COLUMN_MAPPING_BY_COLUMN_MAPPING_ID.format(columnMappingId=column_mapping_id),cookies=cookies, headers=headers,
                               ep_name=GET_PARTNER_DATA_COLUMN_MAPPING_BY_COLUMN_MAPPING_ID)
        return res


    @allure.step
    def update_partner_data_file_with_mapping(self, file_id=None, payload= None, cookies=None):
        if not cookies:
            cookies = self.cookies
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }
        res = self.service.put(UPDATE_PARTNER_DATA_FILE_WITH_MAPPING.format(fileId=file_id), headers=headers, data=json.dumps(payload),cookies=cookies,
                                ep_name=UPDATE_PARTNER_DATA_FILE_WITH_MAPPING)
        return res

    def create_project_mapping(self, file_id=None, cookies=None):
        if not cookies:
            cookies = self.cookies
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }
        res = self.service.post(PROJECT_MAPPING.format(fileId=file_id), headers=headers, cookies=cookies,
                                ep_name=PROJECT_MAPPING)
        return res


    @allure.step
    def create_user_mapping(self, file_id=None, cookies=None):
        if not cookies:
            cookies = self.cookies
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }
        res = self.service.post(USER_MAPPING.format(fileId=file_id), headers=headers, cookies=cookies,
                                ep_name=USER_MAPPING)
        return res

    @allure.step
    def get_project_mapped_rows_count(self, file_id=None, cookies=None):
        if not cookies:
            cookies = self.cookies
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }

        res = self.service.get(GET_PROJECT_MAPPING_ROWS_COUNT.format(fileId=file_id),cookies=cookies, headers=headers,
                               ep_name=GET_PROJECT_MAPPING_ROWS_COUNT)
        return res

    @allure.step
    def get_user_mapped_rows_count(self, file_id=None, cookies=None):
        if not cookies:
            cookies = self.cookies
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }

        res = self.service.get(GET_USER_MAPPING_ROWS_COUNT.format(fileId=file_id),cookies=cookies, headers=headers,
                               ep_name=GET_USER_MAPPING_ROWS_COUNT)
        return res

    def get_projects_data_mapping_by_file_id(self, file_id=None, cookies=None):
        if not cookies:
            cookies = self.cookies
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }
        res = self.service.get(GET_PROJECT_MAPPING_DOWNLOAD.format(fileId=file_id),cookies=cookies, headers=headers, ep_name=GET_PROJECT_MAPPING_DOWNLOAD)
        return res

    def get_users_data_mapping_by_file_id(self, file_id=None, cookies=None):
        if not cookies:
            cookies = self.cookies
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }
        res = self.service.get(GET_USERS_MAPPING_DOWNLOAD.format(fileId=file_id),cookies=cookies, headers=headers, ep_name=GET_USERS_MAPPING_DOWNLOAD)
        return res

    def get_uploaded_file_status(self, file_id=None, cookies=None):
        if not cookies:
            cookies = self.cookies
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }
        res = self.service.get(GET_UPLOADED_FILE_STATUS.format(fileId=file_id),cookies=cookies, headers=headers, ep_name=GET_UPLOADED_FILE_STATUS)
        return res

