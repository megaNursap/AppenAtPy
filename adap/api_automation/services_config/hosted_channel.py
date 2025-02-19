import json
import numpy as np
import allure
import pandas as pd
import pytest

from adap.api_automation.utils.data_util import save_file_with_content
from adap.api_automation.utils.http_util import HttpMethod
from adap.api_automation.services_config.endpoints.api_proxy_endpoints import *

class HC:

    def __init__(self, api_key, payload=None, custom_url=None, env=None, env_fed=None):

        self.api_key = api_key

        if env is None and custom_url is None:  env = pytest.env
        self.env = env

        if payload:
            self.payload = payload
        else:
            self.payload = {
                'key': api_key
            }
        if not env and not custom_url:  env = pytest.env
        self.env = env

        if custom_url:
            self.url = custom_url
        elif env == "fed":
            if env_fed:
                self.url = FED.format(env_fed)
            elif pytest.customize_fed == 'true':
                self.url = FED_CUSTOMIZE.format(pytest.customize_fed_url)
            else:
                self.url = FED.format(pytest.env_fed)
        else:
            self.url = URL.format(env)

        self.headers = {
            'Content-Type': 'application/json'
        }
        self.service = HttpMethod(self.url, self.payload)

    @allure.step
    def create_channel(self, payload):
        res = self.service.post(CREATE_CHANNEL.format(api_key=self.api_key), headers=self.headers, data=json.dumps(payload), ep_name=CREATE_CHANNEL)
        return res

    @allure.step
    def upload_contributor(self, hostedChannelId, payload):
        res = self.service.post(CONTRIBUTOR.format(api_key=self.api_key, hostedChannelId=hostedChannelId), headers=self.headers,
                                data=json.dumps(payload), ep_name=CONTRIBUTOR)
        return res

    @allure.step
    def upload_list_of_contributors(self,file_name):
        files =  {'file':  (file_name, open(file_name, 'rb'))}
        res = self.service.post(UPLOAD_CONTRIBUTORS.format(api_key=self.api_key), verify=False,  headers={}, data={}, files=files, ep_name=UPLOAD_CONTRIBUTORS)
        return res


    @allure.step
    def download_hc(self, channel_id):
        res = self.service.get(DOWNLOAD_CONTRIBUTORS.format(api_key=self.api_key, hostedChannelId=channel_id), ep_name=DOWNLOAD_CONTRIBUTORS)
        return res

    @allure.step
    def update_metedata_for_contributor(self, email, payload):
        res = self.service.put(UPDATE_METADATA.format(api_key=self.api_key, email=email),
                               data=json.dumps(payload),
                               ep_name=UPDATE_METADATA)
        return res

    @allure.step
    def validate_metadata_for_contributor(self, email, metadata_payload, csv_df):
        for param, value in metadata_payload.items():
            if value: assert csv_df.loc[csv_df['email'] == email, param].values, "Value %s has not been found for parameter %s" % (value, param)
            current_value = csv_df.loc[csv_df['email'] == email, param].values[0]

            assert current_value == value, "%s: Expected value - %s, actual - %s " % (param, value, current_value)

    @allure.step
    def download_channel_and_validate_metadata(self, channel_id, email, expected_result, tmpdir):
        res = self.download_hc(channel_id)
        file_name = tmpdir + '/temp_metadata.csv'
        save_file_with_content(file_name, res.content)
        data = pd.read_csv(file_name)
        data.replace(np.NaN, '', inplace=True)
        self.validate_metadata_for_contributor(email, expected_result, data)

    @allure.step
    def update_list_of_contributors(self, file_name):
        files = {'file': (file_name, open(file_name, 'rb'))}
        res = self.service.put(UPLOAD_CONTRIBUTORS.format(api_key=self.api_key), headers={}, data={},
                                files=files, ep_name=UPLOAD_CONTRIBUTORS)
        return res

    @allure.step
    def delete_channel(self, channel_id):
        res = self.service.delete(DELETE_CHANNEL.format(api_key=self.api_key, hostedChannelId=channel_id), headers=self.headers,  ep_name=DELETE_CHANNEL)
        return res

    @allure.step
    def delete_list_of_contributors(self, channel_id, file_name):
        files = {'file': (file_name, open(file_name, 'rb'))}
        res = self.service.delete(DELETE_LIST_CONTRIBUTORS.format(api_key=self.api_key, hostedChannelId=channel_id),
                                  headers={}, data={},
                                  files=files, ep_name=DELETE_LIST_CONTRIBUTORS)
        return res

    @allure.step
    def update_channel_name(self, channel_id, payload):
        res = self.service.put(UPDATE_CHANNEL_NAME.format(api_key=self.api_key, hostedChannelId=channel_id),
                               headers=self.headers, data=json.dumps(payload), ep_name=UPDATE_CHANNEL_NAME)
        return res

