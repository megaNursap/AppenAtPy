from urllib import parse

import requests
from bs4 import BeautifulSoup

from adap.api_automation.utils.http_util import HttpMethod
from adap.api_automation.services_config.endpoints.rp_endpoints import *
from adap.api_automation.services_config.endpoints.client import URL as client_url
import pytest
import allure
import logging
import json

from adap.settings import Config

LOGGER = logging.getLogger(__name__)



def get_sid_cookies(env, username, password):
    url = client_url.format(env=env)

    login_page = requests.get(f'{url}/sessions/new', headers={"Accept": "text/html"}, allow_redirects=False)
    soup = BeautifulSoup(login_page.text, features='html.parser')
    csrf_token = soup.find("meta", {"name": "csrf-token"})['content']

    params = {
        "authenticity_token": csrf_token,
        "session[email]": username,
        "session[password]": password
    }

    headers = {
        'Accept': "text/html",
        'Content-Type': "application/x-www-form-urlencoded",
        # 'Origin': 'https://client.integration.cf3.us'
        'Origin': f'{url}'
    }

    cookies = {
        '_make_session': login_page.cookies['_make_session']
    }

    result = requests.post(f'{url}/sessions', cookies=cookies, data=params, headers=headers, allow_redirects=False)
    return result.cookies


class RP:
    def __init__(self, jwt_token=None, custom_url=None, payload=None, env=None, service=None, refs_token=None,
                 cookies=None):
        self.jwt_token = jwt_token
        self.refs_token = refs_token
        self.payload = payload
        self.cookies = cookies

        if env is None and custom_url is None: env = pytest.env
        self.env = env
        self.origin = ''
        if custom_url is not None:
            self.url = custom_url
        # elif env == "staging":
        #     self.url = STAGING
        elif env == "fed":
            if pytest.customize_fed == 'true':
                self.url = FED_CUSTOMIZE.format(pytest.customize_fed_url)
            else:
                self.url = FED.format(pytest.env_fed)
        elif env != "live":
            self.url = URL.format(env)
            self.origin = client_url
        else:
            self.url = PROD

        self.service = service or HttpMethod()
        self.service.base_url = self.url
        self.service.payload = self.payload

    @allure.step
    def get_valid_sid(self, username, password):
        self.cookies = get_sid_cookies(self.env, username, password)
        return self.cookies

    @allure.step
    def me_endpoint_rp(self):
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Origin": self.origin,
        }
        res = self.service.get(ME_RP, headers=headers, cookies=self.cookies, ep_name=ME_RP)
        return res

    @allure.step
    def switch_api_team_rp(self, team):
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Origin": self.origin,
        }

        res = self.service.post(SWITCH_API_TEAM_RP % team,
                                cookies=self.cookies,
                                headers=headers,
                                ep_name=SWITCH_API_TEAM_RP)
        return res

    @allure.step
    def switch_current_team_rp(self, team):
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Origin": self.origin,
        }
        res = self.service.post(SWITCH_CURRENT_TEAM_RP % team,
                                headers=headers,
                                cookies=self.cookies,
                                ep_name=SWITCH_CURRENT_TEAM_RP)

        return res

    @allure.step
    def get_org_users_rp(self, org_id, email=None, jwt_token=None):
        headers = {
            "x-cf-jwt-token": self.set_jwt_token(jwt_token),
            "Origin": self.origin
        }

        if email is not None:
            res = self.service.get(USER_IN_ORG_RP % org_id + '?email=%s' % email,
                                   headers=headers,
                                   cookies=self.cookies,
                                   ep_name=USER_IN_ORG_RP)
        else:
            res = self.service.get(USER_IN_ORG_RP % org_id,
                                   headers=headers,
                                   cookies=self.cookies,
                                   ep_name=USER_IN_ORG_RP)
        return res

    @allure.step
    def update_job_contributor_level(self, job_id, level, jwt_token=None):
        headers = {
            "x-cf-jwt-token": self.set_jwt_token(jwt_token),
            "content-type": "application/json",
            "Origin": self.origin
        }
        payload = {"name": level}
        res = self.service.put(
            LEVEL % job_id,
            headers=headers,
            data=json.dumps(payload),
            cookies=self.cookies,
            ep_name=LEVEL)
        return res

    @allure.step
    def update_ontology(self, job_id, ontology: list, jwt_token=None):
        headers = {
            "x-cf-jwt-token": self.set_jwt_token(jwt_token),
            "content-type": "application/json",
            "Origin": self.origin
        }
        res = self.service.put(
            ONTOLOGY % job_id,
            headers=headers,
            data=json.dumps(ontology),
            cookies=self.cookies,
            ep_name=ONTOLOGY)
        return res

    @allure.step
    def get_session(self, payload):
        res = self.service.post(JWT_SESSION,
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=JWT_SESSION)
        return res

    @allure.step
    def get_jwt_from_session(self, session_id):
        headers = {
            "x-cf-sid": session_id
        }
        res = self.service.get(ME_RP,
                               headers=headers,
                               cookies=self.cookies,
                               ep_name=ME_RP)
        return res

    @allure.step
    def get_units(self, job_id, params={}):
        """
        params:
            limit (int),
            offset (int),
            sortColumn (str),
            sortDirection (str)
        """
        _params = {
            'limit': 25,
            'offset': 0,
            'sortColumn': 'id',
            'sortDirection': 'desc'
        }
        _params.update(params)
        headers = {
            "x-cf-jwt-token": self.jwt_token,
            "content-type": "application/json",
            "Origin": self.origin
        }
        res = self.service.get(
            UNITS.format(job_id=job_id),
            headers=headers,
            params=_params,
            cookies=self.cookies,
            ep_name=UNITS)
        return res

    @allure.step
    def get_video_frame(self, video_id, frame_id):
        headers = {
            "Origin": self.origin,
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        uri = VIDEO_FRAME.format(
            video_id=video_id,
            frame_id=frame_id
        )
        resp = self.service.get(
            uri,
            cookies=self.cookies,
            ep_name=VIDEO_FRAME)
        return resp

    @allure.step
    def order_test_questions(self, job_id, authenticity_token, question_count, custom_channels):
        uri = ORDER_TEST_QUESTIONS.format(
            job_id=job_id
        )
        headers = {
            "x-cf-jwt-token": self.jwt_token,
            "content-type": "application/json",
            "Origin": self.origin
        }
        payload = {
            "authenticityToken": authenticity_token,
            "questionCount": question_count,
            "customChannels": custom_channels
        }
        resp = self.service.post(
            uri,
            data=json.dumps(payload),
            headers=headers,
            cookies=self.cookies,
            ep_name=ORDER_TEST_QUESTIONS)
        return resp

    def get_judgment_link_text_annotation(self, job_id, annotation_id):
        headers = {
            # "x-cf-jwt-token": self.set_jwt_token(jwt_token),
            "content-type": "application/json",
            "Origin": self.origin
        }
        res = self.service.get(Get_JUDGMENT_LINK % (job_id, annotation_id),
                               headers=headers,
                               cookies=self.cookies,
                               ep_name=Get_JUDGMENT_LINK)
        return res

    @allure.step
    def get_judgment_link_contributor_proxy_text_annotation(self, job_id, annotation_id):
        headers = {
            # "x-cf-jwt-token": self.set_jwt_token(jwt_token),
            "content-type": "application/json",
            "Origin": self.origin
        }
        res = self.service.get(Get_JUDGMENT_LINK_CONTRIBUTOR_PROXY % (job_id, annotation_id),
                               headers=headers,
                               cookies=self.cookies,
                               ep_name=Get_JUDGMENT_LINK_CONTRIBUTOR_PROXY)
        return res

    @allure.step
    def post_grade_link_text_annotation(self, payload, x_storage_refs_token):
        headers = {
            # "x-cf-jwt-token": self.set_jwt_token(jwt_token),
            "x-storage-refs-token": x_storage_refs_token,
            "content-type": "application/json",
            "Origin": self.origin
        }
        res = self.service.post(POST_GRADE_LINK,
                                headers=headers,
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=POST_GRADE_LINK)
        return res

    @allure.step
    def post_accuracy_details_text_annotation(self, payload, x_storage_refs_token=None):
        headers = {
            # "x-cf-jwt-token": self.set_jwt_token(jwt_token),
            "x-storage-refs-token": x_storage_refs_token,
            "content-type": "application/json",
            "Origin": self.origin
        }
        res = self.service.post(POST_ACCURACY,
                                headers=headers,
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=POST_ACCURACY)
        return res

    @allure.step
    def post_aggregation_report_text_annotation(self, payload, x_storage_refs_token, jwt_token=None):
        headers = {
            # "x-cf-jwt-token": self.set_jwt_token(jwt_token),
            "x-storage-refs-token": x_storage_refs_token,
            "content-type": "application/json",
            "Origin": self.origin
        }
        res = self.service.post(POST_AGGREGATION,
                                headers=headers,
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=POST_AGGREGATION)
        return res

    @allure.step
    def post_predict_text_annotation(self, payload, x_storage_refs_token, jwt_token=None):
        headers = {
            # "x-cf-jwt-token": self.set_jwt_token(jwt_token),
            "x-storage-refs-token": x_storage_refs_token,
            "Accept": "application/json",
            "content-type": "application/json",
            "Origin": self.origin
        }
        res = self.service.post(POST_PREDICT,
                                headers=headers,
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=POST_PREDICT)
        return res

    @allure.step
    def post_contributor_proxy_save_annotation_text_annotation(self, payload, jwt_token=None):
        # headers = {
        #     "x-cf-jwt-token": self.set_jwt_token(jwt_token),
        #     "content-type": "application/json",
        #     "Origin" : self.origin
        # }
        res = self.service.post(POST_CONTRIBUTOR_PROXY_SAVE_ANNOTATION,
                                # headers=headers,
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=POST_CONTRIBUTOR_PROXY_SAVE_ANNOTATION)
        return res

    @allure.step
    def post_refs_url(self, payload, refs_token=None):
        if refs_token is None:
            refs_token = self.refs_token
        headers = {
            "x-storage-refs-token": refs_token,
            # "x-cf-jwt-token": self.set_jwt_token(jwt_token),
            "content-type": "application/json"
        }
        res = self.service.post(POST_REFS_URL,
                                data=json.dumps(payload),
                                headers=headers,
                                cookies=self.cookies,
                                ep_name=POST_REFS_URL)
        return res

    @allure.step
    def post_contributor_proxy_save_annotation_super_saver(self, payload, jwt_token=None):
        # headers = {
        #     "x-cf-jwt-token": self.set_jwt_token(jwt_token),
        #     "content-type": "application/json"
        # }
        res = self.service.post(POST_CONTRIBUTOR_PROXY_SUPER_SAVER,
                                # headers=headers,
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=POST_CONTRIBUTOR_PROXY_SAVE_ANNOTATION)
        return res

    @allure.step
    def get_aggregations_distribution(self, job_id, jwt_token=None):
        # headers = {
        #     "x-cf-jwt-token": self.set_jwt_token(jwt_token),
        #     "content-type": "application/json"
        # }
        return self.service.get(GET_JOB_AGGREGATIONS_DISTRIBUTION.format(job_id=job_id),
                                # headers=headers,
                                cookies=self.cookies)

    @allure.step
    def get_audit_info_for_unit(self, job_id, unit_id, jwt_token=None):
        # headers = {
        #     "x-cf-jwt-token": self.set_jwt_token(jwt_token),
        #     "content-type": "application/json"
        # }
        return self.service.get(GET_UNIT_AUDIT_INFORMATION.format(job_id=job_id, unit_id=unit_id),
                                cookies=self.cookies,
                                # headers=headers
                                )

    @allure.step
    def generate_aggregation(self, job_id, jwt_token=None):
        # headers = {
        #     "x-cf-jwt-token": self.set_jwt_token(jwt_token),
        #     "content-type": "application/json"
        # }
        res = self.service.post(GENERATE_AGGREGATION_IPA.format(job_id=job_id),
                                # headers=headers,
                                cookies=self.cookies,
                                ep_name=GENERATE_AGGREGATION_IPA)
        return res

    @allure.step
    def search_unit_for_audit(self, job_id, payload, jwt_token=None):
        # headers = {
        #     "x-cf-jwt-token": self.set_jwt_token(jwt_token),
        #     "content-type": "application/json"
        # }
        return self.service.post(SEARCH_UNITS.format(job_id=job_id),
                                 data=json.dumps(payload),
                                 cookies=self.cookies,
                                 # headers=headers,
                                 ep_name=SEARCH_UNITS)

    @allure.step
    def add_audit(self, job_id, unit_id, payload, jwt_token=None):
        # headers = {
        #     "x-cf-jwt-token": self.set_jwt_token(jwt_token),
        #     "content-type": "application/json"
        # }
        return self.service.put(PUT_AUDIT_INFO_TO_UNIT.format(job_id=job_id, unit_id=unit_id),
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                # headers=headers,
                                ep_name=PUT_AUDIT_INFO_TO_UNIT)

    @allure.step
    def generate_ipa_report(self, job_id, jwt_token=None):
        # headers = {
        #     "x-cf-jwt-token": self.set_jwt_token(jwt_token),
        #     "content-type": "application/json"
        # }
        return self.service.post(IPA_REPORT.format(job_id=job_id),
                                 # headers=headers,
                                 cookies=self.cookies,
                                 ep_name=IPA_REPORT)

    @allure.step
    def get_ipa_report_status(self, job_id, version, jwt_token=None):
        # headers = {
        #     "x-cf-jwt-token": self.set_jwt_token(jwt_token),
        #     "content-type": "application/json"
        # }
        return self.service.get(IPA_REPORT_VERSION.format(job_id=job_id, version=version),
                                cookies=self.cookies,
                                # headers=headers,
                                ep_name=IPA_REPORT)

    @allure.step
    def get_ipa_all_judgments(self, job_id, unit_id, jwt_token=None):
        # headers = {
        #     "x-cf-jwt-token": self.set_jwt_token(jwt_token),
        #     "content-type": "application/json"
        # }
        return self.service.get(ALL_JUDGMENTS.format(job_id=job_id, unit_id=unit_id),
                                # headers=headers,
                                cookies=self.cookies,
                                ep_name=ALL_JUDGMENTS)

    @allure.step
    def get_ipa_audit_aggregation_status(self, job_id):
        return self.service.get(AUDIT_AGGREGATION_STATUS.format(job_id=job_id),
                                cookies=self.cookies,
                                ep_name=AUDIT_AGGREGATION_STATUS)

    @allure.step
    def wait_until_regenerate_aggregation(self, status, job_id, max_wait=500):
        interval = 1
        _c = 0
        while _c < max_wait:
            res = self.get_ipa_audit_aggregation_status(job_id)
            completed_status = res.json_response
            logging.info(completed_status)
            if completed_status[status] is None:
                break
            else:
                _c += interval
        else:
            msg = f'Max wait time reached, ' \
                  f'job {job_id} status: {status}, ' \
                  f'present in : {completed_status}'
            raise Exception(msg)


    @allure.step
    def update_reports_options(self, job_id, payload):
        uri = REPORT_OPTIONS.format(
            job_id=job_id
        )
        # headers = {
        #     "x-cf-jwt-token": self.jwt_token,
        #     "content-type": "application/json",
        #     'accept': '*/*'
        # }

        resp = self.service.put(
            uri,
            data=payload,
            # headers=headers,
            ep_name=REPORT_OPTIONS,
            cookies=self.cookies

        )
        return resp

    @allure.step
    def get_taxonomy_link_to_cds_bucket(self, job_id, teamid, custom_uuid, path_param='pass'):
        params = self.set_taxonomy_param_for_cds_bucket(job_id, teamid, path_param, custom_uuid)
        return self.service.get(TAXONOMY_GET_LINK,
                                cookies=self.cookies,
                                ep_name=TAXONOMY_GET_LINK,
                                params=params)

    @allure.step
    def get_taxonomy_link_shared_file(self, job_id, teamid, path_param='pass'):
        params = self.set_taxonomy_to_shared_file(job_id, teamid, path_param)
        return self.service.get(TAXONOMY_GET_LINK,
                                cookies=self.cookies,
                                ep_name=TAXONOMY_GET_LINK,
                                params=params)

    @allure.step
    def put_taxonomy_link_shared_file(self, job_id, team_id, path_param='pass'):
        params = self.set_taxonomy_to_shared_file(job_id, team_id, path_param)
        return self.service.get(TAXONOMY_PUT_LINK,
                                cookies=self.cookies,
                                ep_name=TAXONOMY_PUT_LINK,
                                params=params)

    @allure.step
    def put_taxonomy_link_bucket_uuid(self, job_id, team_id, custom_uuid, path_param='pass'):
        params = self.set_taxonomy_param_for_cds_bucket(job_id, team_id, path_param, custom_uuid)
        return self.service.get(TAXONOMY_PUT_LINK,
                                cookies=self.cookies,
                                ep_name=TAXONOMY_PUT_LINK,
                                params=params)

    @allure.step
    def delete_taxonomy_link_bucket_uuid(self, job_id, teamid, custom_uuid, path_param='pass'):
        params = self.set_taxonomy_param_for_cds_bucket(job_id, teamid, path_param, custom_uuid)
        return self.service.get(TAXONOMY_DELETE_LINK,
                                cookies=self.cookies,
                                ep_name=TAXONOMY_DELETE_LINK,
                                params=params)

    @allure.step
    def post_taxonomy_url(self, job_id, teamId, path_param='path'):
        params = self.set_taxonomy_param(job_id, teamId, path_param)
        return self.service.post(TAXONOMY_URL.format(job_id=job_id),
                                 cookies=self.cookies,
                                 ep_name=TAXONOMY_URL,
                                 params=params)

    @allure.step
    def get_taxonomy_url(self, job_id, team_id, path_param='path'):
        params = self.set_taxonomy_param(job_id, team_id, path_param)
        return self.service.get(TAXONOMY_URL.format(job_id=job_id),
                                cookies=self.cookies,
                                ep_name=TAXONOMY_URL,
                                params=params)

    @allure.step
    def upload_taxonomy_file(self, json_file, job_id, team_id, custom_uuid, name='taxonomy_1'):
        with open(json_file) as fjson:
            headers = {"Content-Type": "application/json"}
            res = self.put_taxonomy_link_bucket_uuid(job_id, team_id, custom_uuid)
            res.assert_response_status(200)

            url = res.json_response.get('url')
            request = requests.put(url, data=fjson, headers=headers)
            print(request.status_code)

            res = self.put_taxonomy_link_shared_file(job_id, team_id)
            res.assert_response_status(200)

            param = {custom_uuid: name}
            url = res.json_response.get('url')
            requests.put(url, json=param)

    @allure.step
    def set_jwt_token(self, jwt_token):
        if jwt_token is None:
            jwt_token = self.jwt_token
        return jwt_token

    @allure.step
    def set_taxonomy_param(self, job_id, team_id, path_param):
        path = f"jobs/{job_id}/shared/taxonomies.json"
        path = parse.quote(path)
        return {
            'pass': {'path': path, 'teamId': team_id},
            'teamId': {'path': path, 'teamId': None},
            'path': {'path': None, 'teamId': team_id},
            None: {}
        }[path_param]

    @allure.step
    def set_taxonomy_param_for_cds_bucket(self, job_id, team_id, path_param, bucket_uuid):
        path = f"jobs/{job_id}/shared/taxonomy/{bucket_uuid}.json"
        path = parse.quote(path)
        return {
            'pass': {'path': path, 'teamId': team_id},
            'teamId': {'path': path, 'teamId': None},
            'path': {'path': None, 'teamId': team_id},
            None: {}
        }[path_param]

    @allure.step
    def set_taxonomy_to_shared_file(self, job_id, team_id, path_param):
        path = f"jobs/{job_id}/shared/taxonomies.json"
        path = parse.quote(path)
        return {
            'pass': {'path': path, 'teamId': team_id},
            'teamId': {'path': path, 'teamId': None},
            'path': {'path': None, 'teamId': team_id},
            None: {}
        }[path_param]

    @allure.step
    def get_team_settings(self, team_id):
        res = self.service.get(TEAM_SETTINGS.format(team_id=team_id), cookies=self.cookies)
        return res

    def put_team_settings(self, team_id, payload):
        res = self.service.put(TEAM_SETTINGS.format(team_id=team_id), data=json.dumps(payload) ,cookies=self.cookies)
        return res

