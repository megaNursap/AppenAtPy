import json
import os
import time

from urllib3 import encode_multipart_formdata

from adap.api_automation.services_config.endpoints.report_endpoints import *
from adap.api_automation.utils.data_util import get_data_file
from adap.api_automation.utils.http_util import HttpMethod, ApiHeaders
from adap.api_automation.services_config.endpoints.builder_endpoints import *
from adap.api_automation.services_config.endpoints.user_specific_endpoints import *
from adap.settings import Config
import pytest
import allure
import logging
import urllib
import requests

LOGGER = logging.getLogger(__name__)


def find_all_jobs_with_status_for_user(api_key):
    job = Builder(api_key)

    page = 1
    jobs = job.get_jobs_for_user()
    count_job = len(jobs.json_response)

    _jobs = {}

    while count_job > 0:
        for current_job in jobs.json_response:
            job.job_id = current_job['id']
            res = job.get_json_job_status()
            if _jobs.get(res.json_response['state']) is not None:
                jobs_with_status = _jobs[res.json_response['state']]
                jobs_with_status.append(job.job_id)
                _jobs[res.json_response['state']] = jobs_with_status
            else:
                _jobs[res.json_response['state']] = [job.job_id]

        page += 1
        jobs = job.get_jobs_for_user(page=page)
        count_job = len(jobs.json_response)
    print("-----")
    print(_jobs)

    return _jobs


class Builder:

    def __init__(self, api_key, payload=None, custom_url=None, api_version='v1', env=None, job_id='', env_fed=None):

        self.api_key = api_key
        self.job_id = job_id
        self.jobs_id = []
        self.api_version = api_version
        self.payload = payload

        if env is None and custom_url is None:  env = pytest.env

        self.env = env

        if custom_url is not None:
            self.url = custom_url
        elif env == "live":
            self.url = PROD
        elif env == "fed":
            if pytest.customize_fed == 'true':
                self.url = FED_CUSTOMIZE.format(pytest.customize_fed_url)
            elif env_fed:
                self.url = FED.format(env_fed)
            else:
                self.url = FED.format(pytest.env_fed)
        elif env == "hipaa":
            self.url = HIPAA
        # elif env == "staging":
        #     if api_version == 'v1':
        #         self.url = STAGING
        #     else:
        #         self.url = STAGING_V2
        else:
            if api_version == 'v1':
                self.url = URL.format(env)
            elif api_version == 'v2':
                self.url = URL_V2.format(env)
            else:
                self.url = API_BETA_V2.format(env)

        self.service = HttpMethod(self.url, self.payload)
        self.headers = {
            "Content-Type": "application/json",
            "AUTHORIZATION": "Token token={token}".format(token=self.api_key)
        }

# TODO: remove key as a query param for /v2/job endpoint
    @allure.step
    def create_job(self, team_id=None):
        if self.api_version == 'v2':
            URL = JOB_V2
        else:
            URL = JOB

        if team_id:
            endpoint = URL
            params = {
                "job[team_id]": team_id
            }
            res = self.service.post(endpoint, params=params, ep_name=URL, headers=self.headers)
        else:
            res = self.service.post(URL, ep_name=URL, headers=self.headers,  verify=False)

        self.job_id = res.json_response.get('id')
        if os.environ.get("PYTEST_CURRENT_TEST", ""):
            if res.status_code == 200:
                pytest.data.job_collections[self.job_id] = self.api_key
        return res

    @allure.step
    def create_job_with_json(self, json_file, payload=None):
        with open(json_file) as fjson:
            if payload:
                res = self.service.post(UPLOAD_JSON, params=payload, data=fjson, ep_name=UPLOAD_JSON, headers=self.headers)
            else:
                res = self.service.post(UPLOAD_JSON, data=fjson, ep_name=UPLOAD_JSON, headers=self.headers)

            self.job_id = res.json_response.get('id')
            if os.environ.get("PYTEST_CURRENT_TEST"):
                if res.status_code == 200:
                    pytest.data.job_collections[self.job_id] = self.api_key
            return res

    @allure.step
    def create_job_with_cml(self, cml=None):
        payload = {
            'key': self.api_key,
            'job': {
                'title': "Smoke Test Simple",
                'instructions': "instructions",
                'project_number': 'PN000112',
                'cml': cml
            }
        }
        self.payload = payload
        self.service = HttpMethod(self.url, self.payload, self.headers)
        resp = self.create_job()
        assert resp.status_code == 200
        return resp

    @allure.step
    def create_job_with_csv(self, data, payload=None):
        headers = {'Content-Type': 'text/csv', "AUTHORIZATION": "Token token={token}".format(token=self.api_key)}
        with open(data, buffering=1) as file:
            data = file.read()

        if payload:
            res = self.service.post(UPLOAD_JSON, data=data.encode('utf-8'), headers=headers,
                                    params=payload,
                                    ep_name=UPLOAD_JSON)
        else:
            res = self.service.post(UPLOAD_JSON, data=data.encode('utf-8'), headers=headers,
                                    ep_name=UPLOAD_JSON)

        self.job_id = res.json_response.get('id')
        if os.environ.get("PYTEST_CURRENT_TEST"):
            if res.status_code == 200:
                pytest.data.job_collections[self.job_id] = self.api_key
        time.sleep(5)
        return res

    @allure.step
    def upload_data(self, data, job_id=None, data_type='json', large_file=False, params=None):

        if data_type == 'csv':
            headers = {'Content-Type': 'text/csv',
                       "AUTHORIZATION": "Token token={token}".format(token=self.api_key)}
            params = {'force': 'true'}
        else:
            headers = {'Content-Type': 'application/json',
                       "AUTHORIZATION": "Token token={token}".format(token=self.api_key)}
            params = {'force': 'true'}

        if not job_id: job_id = self.job_id

        with open(data) as file:
            data = file.read()

        if large_file:
            _s = requests.session()
            _s.verify = False
            url = URL.format(self.env) + UPLOAD_FILE_TO_JOB % job_id

            res = _s.put(
                url=url,
                headers=headers,
                params=params,
                data=data.encode('utf-8')
            )
        else:
            res = self.service.put(UPLOAD_FILE_TO_JOB % job_id, headers=headers, params=params,
                                   data=data.encode('utf-8'), ep_name=UPLOAD_FILE_TO_JOB)

        return res

    @allure.step
    def copy_job(self, job_id, param=None):
        endpoint = (COPY % job_id)
        if param:
            endpoint += '%s=true' % param

        res = self.service.get(endpoint, ep_name=COPY, headers=self.headers)
        self.job_id = res.json_response.get('id')
        if os.environ.get("PYTEST_CURRENT_TEST"):
            if res.status_code == 200:
                pytest.data.job_collections[self.job_id] = self.api_key
        return res

    @allure.step
    def copy_template_job(self, job_id, template_id=None, team_id=None):
        endpoint = (COPY_TEMPLATE % job_id) + 'template_id=%s' % template_id
        if team_id:
            endpoint += '&team_id=%s' % team_id

        res = self.service.get(endpoint, ep_name=COPY_TEMPLATE, headers=self.headers)
        self.job_id = res.json_response.get('id')
        if os.environ.get("PYTEST_CURRENT_TEST"):
            if res.status_code == 200:
                pytest.data.job_collections[self.job_id] = self.api_key
        return res

    @allure.step
    def update_job(self, job_id=None, payload=None):
        if not job_id:
            job_id = self.job_id
        if payload:
            payload = json.dumps(payload)
        res = self.service.put(UPDATE % job_id, data=payload, ep_name=UPDATE, headers=self.headers)
        return res

    @allure.step
    def get_rows_in_job(self, job_id=None):
        job_id = job_id if job_id else self.job_id
        res = self.service.get(ROWS % job_id, ep_name=ROWS, headers=self.headers)
        return res

    @allure.step
    def change_state_of_row(self, unit_id=None, status=None):
        params = {
            'unit': {
                'state': status
            }
        }
        res = self.service.put(UPDATE_UNIT % (self.job_id, unit_id), data=json.dumps(params), ep_name=UPDATE_UNIT,
                               headers=self.headers)
        return res

    @allure.step
    def update_job_settings_list(self, attribute: str, values: list):
        params = {
            'job': {
                attribute: values
            }
        }
        res = self.service.put(UPDATE % self.job_id, data=json.dumps(params), ep_name=UPDATE, headers=self.headers)
        return res

    @allure.step
    def split_column(self, column=None, delimiter=None):
        res = self.service.get(SPLIT_UNITS % (self.job_id, column, delimiter), ep_name=SPLIT_UNITS, headers=self.headers)
        return res

    @allure.step
    def count_rows(self, job_id=None, delay=4):
        time.sleep(delay)
        job_id = job_id if job_id else self.job_id
        res = self.service.get(ROW_COUNT % job_id, ep_name=ROW_COUNT, headers=self.headers)
        return res

    @allure.step
    def add_new_row(self, job_id=None, data=None):
        job_id = job_id if job_id else self.job_id
        payload = {
                   'unit': {
                       'data': data
                   }
                   }
        res = self.service.post(ADD_ROW % job_id, data=json.dumps(payload), ep_name=ADD_ROW, headers=self.headers)
        return res

    @allure.step
    def cancel_unit(self, unit_id=None):
        res = self.service.post(CANCEL_UNIT % (self.job_id, unit_id), ep_name=CANCEL_UNIT, headers=self.headers)
        return res

    @allure.step
    def delete_unit(self, unit_id=None):
        res = self.service.delete(DELETE_UNIT % (self.job_id, unit_id), ep_name=DELETE_UNIT, headers=self.headers)
        return res

    @allure.step
    def get_unit(self, unit_id=None, job_id=None):
        job_id = job_id or self.job_id
        res = self.service.get(UNIT % (job_id, unit_id), ep_name=UNIT, headers=self.headers)
        return res

    @allure.step
    def convert_uploaded_tq(self, max_retries=0, wait_time=5):
        c_retries = 0
        while c_retries <= max_retries:
            ep = CONVERT_UPLOADED_TQ % self.job_id
            res = self.service.put(ep, ep_name=CONVERT_UPLOADED_TQ, headers=self.headers)
            if res.status_code == 200:
                return res
            else:
                LOGGER.error(f"convert_uploaded_tq {ep} "
                             f"returned {res.status_code}, "
                             f"retry in {wait_time} seconds")
                c_retries += 1
                time.sleep(wait_time)
        return res

    @allure.step
    def delete_job(self, job_id=None):
        """
        method deprecated https://appen.atlassian.net/browse/ADAP-3613
        """
        headers = {
                "Accept": "application/json",
                "AUTHORIZATION": "Token token={token}".format(token=self.api_key)
            }

        job_id = job_id if job_id else self.job_id

        return self.service.delete(DELETE % job_id, headers=headers, ep_name=DELETE)

    @allure.step
    def get_jobs_for_user(self, page=1, team_id=None):
        """
        JSON representation of the latest 10 Jobs.  Use page={n} query to get additional Jobs
        """
        team = ''
        if team_id is not None:
            team = "&team_id=%s" % team_id
        res = self.service.get(JOB + ('?page=%s' % page) + team, ep_name=JOB, headers=self.headers)
        return res

    @allure.step
    def get_list_of_jobs_id(self, json_jobs):
        ids = [job['id'] for job in json_jobs]
        return ids

    @allure.step
    def get_job_status(self, job_id=None):
        if job_id is None:
            job_id = self.job_id
        res = self.service.get(JOB_STATUS % job_id, ep_name=JOB_STATUS, headers=self.headers)
        LOGGER.debug(f"Response Job Status: %s" % res.json_response)
        return res

    @allure.step
    def add_channel_to_job(self, channel_name):
        LOGGER.debug(f"channel name to enable for job: %s" % channel_name)
        payload = {
            "channels": channel_name
        }
        res = self.service.post(CHANNELS % self.job_id, data=json.dumps(payload), ep_name=CHANNELS, headers=self.headers)
        return res

    @allure.step
    def get_channels_for_job(self):
        res = self.service.get(CHANNELS % self.job_id, ep_name=CHANNELS, headers=self.headers)
        return res

    @allure.step
    def disable_channel_on_job(self, channel_name):
        LOGGER.debug(f"channel name to disable for job: %s" % channel_name)
        payload = {
            "channel_name": channel_name
        }
        res = self.service.post(DISABLE_CHANNEL % self.job_id, params=payload, ep_name=DISABLE_CHANNEL, headers=self.headers)
        return res

    @allure.step
    def get_json_job_status(self, job_id=None):
        if job_id is None:
            job_id = self.job_id
        res = self.service.get(JSON_JOB_STATUS % job_id, ep_name=JSON_JOB_STATUS, headers=self.headers)
        return res

    @allure.step
    def get_job_secret(self, job_id=None):
        secret = self.get_json_job_status(job_id).json_response.get('secret')
        return urllib.parse.quote(secret)

    # not work now
    @allure.step
    def set_job_task_payment(self, payment):
        params = {
            "job[payment_cents]": payment,
        }
        res = self.service.put(SET_TASK_PAYMENT % self.job_id, params=params, ep_name=SET_TASK_PAYMENT, headers=self.headers)
        return res

    @allure.step
    def update_job_settings(self, params):
        res = self.service.put(UPDATE % self.job_id, params=params, ep_name=UPDATE, headers=self.headers)
        return res

    @allure.step
    def update_job_settings_v2(self, payload):
        headers = {'Content-Type': 'application/x-www-form-urlencoded', "AUTHORIZATION": "Token token={token}".format(token=self.api_key)}
        res = self.service.put(UPDATE % self.job_id, data=payload, headers=headers, ep_name=UPDATE)
        return res

    @allure.step
    def launch_job(self, rows=None, external_crowd=False, channel="cf_internal"):

        if not rows:
            count_res = self.count_rows()
            rows = count_res.json_response['count']

        params = {
            "debit[units_count]": rows,
            "channels[0]": channel,
        }
        if external_crowd:
            params['channels[1]'] = 'on_demand'

        res = self.service.post(LAUNCH_JOB % self.job_id, params=params, ep_name=LAUNCH_JOB, headers=self.headers)

        if res.status_code == 200:
            self.wait_until_status("running")

        return res

    @allure.step
    def auto_launch(self):
        params = {
            "job[auto_order]": True
        }
        res = self.service.put(UPDATE % self.job_id, data=json.dumps(params), ep_name=UPDATE, headers=self.headers)
        return res

    @allure.step
    def pause_job(self):
        res = self.service.get(PAUSE_JOB % self.job_id, ep_name=PAUSE_JOB, headers=self.headers)
        self.wait_until_status("paused")
        return res

    @allure.step
    def resume_job(self):
        res = self.service.get(RESUME_JOB % self.job_id, ep_name=RESUME_JOB, headers=self.headers)
        self.wait_until_status("running")
        return res

    @allure.step
    def cancel_job(self, job_id=None):
        job_id = job_id if job_id else self.job_id

        res = self.service.get(CANCEL_JOB % job_id, ep_name=CANCEL_JOB, headers=self.headers)
        if res.json_response != {'error': "You can't cancel a job that hasn't been launched."}:
            self.wait_until_status("canceled")
        return res

    @allure.step
    def restore_job(self, job_id=None):
        res = self.service.post(RESTORE_JOB % job_id, ep_name=RESTORE_JOB, headers=self.headers)
        return res

    def wait_until_status(self, status, max_time=0):
        if not max_time:
            max_time = Config.MAX_WAIT_TIME
        wait = 2
        running_time = 0
        current_status = ""
        while (current_status != status) and (running_time < max_time):
            res = self.get_json_job_status()
            res.assert_response_status(200)
            current_status = res.json_response['state']
            running_time += wait
            time.sleep(wait)

    def wait_until_status2(self, status, key='state', state_key=None):
        max_wait = Config.MAX_WAIT_TIME
        interval = 10
        _c = 0
        while _c < max_wait:
            res = self.get_json_job_status()
            res.assert_response_status(200)
            if state_key:
                _status = res.json_response[key][state_key]
            else:
                _status = res.json_response[key]

            if _status == status:
                break
            else:
                _c += interval
                time.sleep(interval)
        else:
            msg = f'Max wait time reached, ' \
                  f'job {self.job_id} status: {_status}, ' \
                  f'expected status: {status}'
            raise Exception(msg)

    def wait_until_golds_count(self, count, max_time=0):
        if not max_time:
            max_time = Config.MAX_WAIT_TIME
        wait = 5
        running_time = 0
        current_count = 0
        while (current_count != count) and (running_time < max_time):
            res = self.get_json_job_status()
            res.assert_response_status(200)
            current_count = res.json_response['golds_count']
            running_time += wait
            time.sleep(wait)

    @allure.step
    def create_simple_job(self, shapes=None, aggregation=None, cml=None):
        cml_sample = '''
                       <div class="html-element-wrapper">
                         <span>{{text}}</span>
                       </div>
                       <cml:radios label="Is this funny or not?" validates="required" gold="true">
                         <cml:radio label="funny" value="funny" />
                         <cml:radio label="not funny" value="not_funny" />
                       </cml:radios>
                  '''
        shapes_cml = '''
        <cml:shapes type="['box']" source-data="{{image_url}}" validates="required" ontology="true" name="annotation" 
        label="Annotate this image" class-threshold="0.7" box-threshold="0.7" class-agg="agg" box-agg="0.7"/>
        '''
        aggregation_cml = '''
                             <cml:group multiple="true" aggregation="true" group_name="group1" >
                             <cml:text name="first_name" label="First Name:" aggregation="all"></cml:text>
                             <cml:text name="last_name" label="Last Name:" validates="required"></cml:text>
                             </cml:group>
                              '''
        if shapes:
            payload = {
                'job': {
                    'title': "Smoke Test Simple",
                    'instructions': "instructions",
                    'project_number': 'PN000112',
                    'cml': shapes_cml
                }
            }
            add_file = get_data_file("/animal_urls.json", env=self.env)
        elif aggregation:
            if cml:
                aggregation_cml = cml
            payload = {
                'job': {
                    'title': "cml aggregation job",
                    'instructions': "instructions",
                    'project_number': 'PN000112',
                    'cml': aggregation_cml
                }
            }
            add_file = get_data_file('/sample_data.json')
        else:
            payload = {
                'job': {
                    'title': "Smoke Test Simple",
                    'instructions': "instructions",
                    'project_number': 'PN000112',
                    'cml': cml_sample
                }
            }
            add_file = get_data_file("/simple_job/simple_data__tq_ex.json", env=self.env)

        self.payload = payload
        self.service = HttpMethod(self.url, self.payload)
        resp = self.create_job()
        if resp.status_code != 200:
            LOGGER.debug("JOB has not been created")
            return False

        # # load data - json
        print("data=", add_file)
        upload_data_rest = self.upload_data(add_file)
        time.sleep(5)
        if upload_data_rest.status_code != 200:
            LOGGER.debug("Data has not been uploaded to %s job" % self.job_id)
            return False

        return True

    @allure.step
    def create_simple_job_no_data(self):
        cml_sample = '''
                           <div class="html-element-wrapper">
                             <span>{{text}}</span>
                           </div>
                           <cml:radios label="Is this funny or not?" validates="required" gold="true">
                             <cml:radio label="funny" value="funny" />
                             <cml:radio label="not funny" value="not_funny" />
                           </cml:radios>
                      '''
        payload = {
            'job': {
                'title': "Smoke Test Simple",
                'instructions': "instructions",
                'project_number': 'PN000112',
                'cml': cml_sample,
                "channels[0]": "cf_internal"
            }
        }
        self.payload = payload
        self.service = HttpMethod(self.url, self.payload)
        resp = self.create_job()
        if resp.status_code != 200:
            LOGGER.debug("JOB has not been created")
            return False
        else:
            return True

    @allure.step
    def create_simple_job_with_test_questions(self, max_time=10):
        self.create_simple_job()
        time.sleep(5)
        # # convert uploaded test questions
        resp = self.convert_uploaded_tq(max_retries=max_time)
        if resp.status_code == 200:
            return True
        else:
            LOGGER.error("TQ's have not been converted for %s job" % self.job_id)
            return False


    @allure.step
    def generate_report(self, payload=None):
        if payload is None:
            payload = self.payload
        res = self.service.get(REPORT % self.job_id, params=payload, allow_redirects=True, ep_name=REPORT,
                               headers=self.headers)
        return res

    @allure.step
    def get_user_teams(self):
        res = self.service.get(TEAMS, ep_name=TEAMS, headers=self.headers)
        return res

    @allure.step
    def regenerate_report(self, payload=None):
        if payload is None:
            payload = self.payload
        res = self.service.post(REGENERATE % self.job_id, params=payload, ep_name=REGENERATE, headers=self.headers)
        return res

    @allure.step
    def get_rows_and_judgements(self, job_id=None):
        if not job_id:
            job_id = self.job_id
        res = self.service.get(ROWS_AND_JUDGEMENTS % (job_id, 1), ep_name=ROWS_AND_JUDGEMENTS, headers=self.headers)
        return res

    @allure.step
    def get_agg_result_per_row(self, unit_id):
        res = self.service.get(AGG_RESULT_FOR_ROW % (self.job_id, unit_id), ep_name=AGG_RESULT_FOR_ROW, headers=self.headers)
        return res

    @allure.step
    def get_all_judgments_per_row(self, unit_id):
        res = self.service.get(ALL_JUDGEMENTS_PER_ROW % (self.job_id, unit_id),
                               ep_name=ALL_JUDGEMENTS_PER_ROW, headers=self.headers)
        return res

    @allure.step
    def get_account_info(self):
        res = self.service.get(ACCOUNT, ep_name=ACCOUNT, headers=self.headers)
        return res

    @allure.step
    def get_job_tags(self):
        res = self.service.get(JOB_TAGS % self.job_id, ep_name=JOB_TAGS, headers=self.headers)
        return res

    @allure.step
    def add_job_tag(self, tag_name):
        params = {
            "tags": tag_name
        }
        res = self.service.post(JOB_TAGS % self.job_id, data=json.dumps(params), ep_name=JOB_TAGS, headers=self.headers)
        return res

    @allure.step
    def replace_job_tags(self, list_tags):
        params = {
            "tags": list_tags
        }
        res = self.service.put(JOB_TAGS % self.job_id, data=json.dumps(params), ep_name=JOB_TAGS, headers=self.headers)
        return res

    """Contributor related methods on a job"""

    @allure.step
    def notify_contributor(self, message, contributor_id):
        params = {
            "message": message
        }
        res = self.service.post(NOTIFY_CONTRIBUTOR % (self.job_id, contributor_id),
                                ep_name=NOTIFY_CONTRIBUTOR,
                                data=json.dumps(params), headers=self.headers)
        return res

    @allure.step
    def pay_bonus_to_contributor(self, contributor_id, amount):
        data = {
            'amount': amount
        }
        res = self.service.post(PAY_CONTRIBUTOR_BONUS % (self.job_id, contributor_id),
                                ep_name=PAY_CONTRIBUTOR_BONUS,
                                data=json.dumps(data), headers=self.headers)
        return res

    @allure.step
    def reject_contributor(self, contributor_id, reason=None):
        params = {
            "reason": reason,
            "manual": True
        }
        res = self.service.put(REJECT_CONTRIBUTOR % (self.job_id, contributor_id),
                               ep_name=REJECT_CONTRIBUTOR,
                               data=json.dumps(params),
                               headers=self.headers)
        return res

    @allure.step
    def flag_contributor(self, contributor_id, flag=None):
        params = {
            "flag": flag
        }
        res = self.service.put(FLAG_CONTRIBUTOR % (self.job_id, contributor_id), data=json.dumps(params),
                               ep_name=FLAG_CONTRIBUTOR, headers=self.headers)
        return res

    @allure.step
    def switch_api_team(self, team_id):
        res = self.service.post(SWITCH_API_TEAM % team_id, ep_name=SWITCH_API_TEAM, headers=self.headers)
        return res

    @allure.step
    def get_legend(self):
        res = self.service.get(LEGEND % self.job_id, ep_name=LEGEND, headers=self.headers)
        return res

    @allure.step
    def filter_jobs(self, params):
        res = self.service.get(JOB, params=params, ep_name=JOB, headers=self.headers)
        return res

    @allure.step
    def get_max_crowd_cost(self):
        res = self.service.get(MAX_CROWD_PAY % self.job_id, ep_name=MAX_CROWD_PAY, headers=self.headers)
        return res

    # TODO: refactor this method. Can probably be simplfies with existing one
    @allure.step
    def create_job_from_payload(self, custom_payload):
        _URL = JOB
        res = self.service.post(_URL, data=json.dumps(custom_payload), headers=self.headers)

        self.job_id = res.json_response.get('id')
        if os.environ.get("PYTEST_CURRENT_TEST", ""):
            if res.status_code == 200:
                pytest.data.job_collections[self.job_id] = self.api_key
        return res

    @allure.step
    def get_balance(self):
        res = self.service.get(GET_BALANCE, ep_name=GET_BALANCE, headers=self.headers)
        return res

    @allure.step
    def get_judgements_json_report(self, job, page=1):
        params = f"?page={page} | jq > {job}_judgments_p{page}.json".format(job=job, page=page)
        res = self.service.get((JUDGMENTS_REPORT % job) + params, ep_name="judgments.json", headers=self.headers)
        return res

    @allure.step
    def upload_taxonomy_file_via_public(self, job_id, api_key, name, file, type_of_file, file_param="file"):
        with open(file) as a_file:
            header = {
                "Accept": "application/json"
            }
            value = {"name": name}
            file_dict = {file_param: ("name", a_file, type_of_file)}
            res = self.service.put((UPLOAD_TAXONOMY % (job_id, api_key)), headers=header, data=value, files=file_dict)

            return res

    @allure.step
    def delete_taxonomy_file_via_public(self, job_id, api_key, name):
        header = {
            "Accept": "application/json"
        }
        value = {"name": name}
        file_dict = {'file': (None, "a_file, type_of_file")}
        res = self.service.delete((UPLOAD_TAXONOMY % (job_id, api_key)), headers=header, data=value, files=file_dict)
        return res


