import json
import os
import time

import allure
import pytest
import requests

from adap.api_automation.services_config.endpoints.quality_flow_endpoints import *
from adap.api_automation.services_config.requestor_proxy import get_sid_cookies
from adap.api_automation.utils.http_util import HttpMethod


def get_unit_by_index(api, project_id, team_id, index):
    payload = {"startRow": 0, "endRow": index + 1, "filterModel": {}, "sortModel": [], "queryString": ""}
    res = api.post_units(project_id=project_id, team_id=team_id, payload=payload)
    return res.json_response['data']['units'][index]


def get_job_attribute(api, team_id, job_id, attribute):
    res = api.get_job_by(team_id, job_id)
    assert res.status_code == 200

    return res.json_response['data'][attribute]


class QualityFlowApi():
    def __init__(self, custom_url=None, payload=None, env=None, api_key=None, session=None):
        self.payload = payload
        if env is None and custom_url is None: env = pytest.env
        self.env = env
        if custom_url:
            self.url = custom_url
        else:
            self.url = URL.format(env)
            self.kepler_internal_api_gateway_url = KEPLER_INTERNAL_API_GATEWAY.format(env)

        self.cookies = None
        self.account = {}
        self.service = HttpMethod(self.url, self.payload, session)
        if api_key:
            self.headers = {
                "Content-Type": "application/json",
                "AUTHORIZATION": "Token token={token}".format(token=api_key)
            }

    @allure.step
    def get_valid_sid(self, username, password):
        self.cookies = get_sid_cookies(self.env, username, password)
        self.account = {'name': username, 'password': password}
        return self.cookies

    @allure.step
    def set_cookies(self, cookies):
        self.cookies = cookies


class QualityFlowApiProject(QualityFlowApi):
    """
    https://api-kepler.integration.cf3.us/project/swagger-ui/index.html#/
    """

    def __init__(self, custom_url=None, payload=None, env=None, api_key=None, session=None):
        super().__init__(custom_url=custom_url, payload=payload, env=env, api_key=api_key, session=session)

    # ------------------------------------------------------------------------------------------
    # ---------------- Project Controller -----------------------------------------------------
    # ------------------------------------------------------------------------------------------

    # deprecated
    # @allure.step
    # def get_list_of_projects(self, team_id, page_num=1, page_size=10):
    #     res = self.service.get(f"{PROJECTS_LIST}"
    #                            f"?pageNum={page_num}"
    #                            f""
    #                            f"&pageSize={page_size}"
    #                            f"&teamId={team_id}",
    #                            cookies=self.cookies,
    #                            ep_name=PROJECTS_LIST)
    #     return res

    @allure.step
    def get_list_of_projects(self, team_id, payload):
        res = self.service.post(f"{PROJECTS_LIST}"
                                f"?teamId={team_id}",
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=PROJECTS_LIST)
        return res

    @allure.step
    def post_create_project(self, team_id, payload):
        res = self.service.post(f"{PROJECT_CREATE}"
                                f"?teamId={team_id}",
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=PROJECT_CREATE)

        if os.environ.get("PYTEST_CURRENT_TEST", ""):
            if res.status_code == 200:
                project = res.json_response['data']
                if project:
                    _account = self.account
                    _account['team_id'] = team_id
                    pytest.data.qf_project_collection.append({'account': _account,
                                                              'project_id': project['id']})

        return res

    @allure.step
    def put_update_project(self, team_id, payload):
        res = self.service.put(f"{PROJECT_UPDATE}"
                               f"?teamId={team_id}",
                               data=json.dumps(payload),
                               cookies=self.cookies,
                               ep_name=PROJECT_UPDATE)
        return res

    @allure.step
    def delete_project(self, project_id, team_id, version_id):
        res = self.service.delete(f"{PROJECT_DELETE}"
                                  f"?projectId={project_id}"
                                  f"&version={version_id}"
                                  f"&teamId={team_id}",
                                  cookies=self.cookies,
                                  ep_name=PROJECT_DELETE)
        return res

    @allure.step
    def get_project_details(self, project_id, team_id):
        res = self.service.get(f"{PROJECT_DETAILS}"
                               f"?projectId={project_id}"
                               f"&teamId={team_id}",
                               cookies=self.cookies,
                               ep_name=PROJECT_DETAILS)

        return res

    @allure.step
    def get_project_data_summary(self, project_id, team_id):
        res = self.service.get(f"{PROJECT_DATA_SUMMARY}"
                               f"?projectId={project_id}"
                               f"&teamId={team_id}",
                               cookies=self.cookies,
                               ep_name=PROJECT_DATA_SUMMARY)

        return res

    # ------------------------------------------------------------------------------------------
    # ---------------- Project File Controller -------------------------------------------------
    # ------------------------------------------------------------------------------------------
    @allure.step
    def get_upload_dataset(self, project_id, team_id, dataset_id):
        res = self.service.get(f"{FILE_DATASET}"
                               f"?projectId={project_id}"
                               f"&teamId={team_id}"
                               f"&datasetId={dataset_id}",
                               cookies=self.cookies,
                               ep_name=FILE_DATASET)

        return res

    @allure.step
    def get_list_of_files_for_project(self, project_id, team_id, page_num=0, page_size=10):
        res = self.service.get(f"{FILES}"
                               f"?projectId={project_id}"
                               f"&teamId={team_id}"
                               f"&pageNum={page_num}"
                               f"&pageSize={page_size}",
                               cookies=self.cookies,
                               ep_name=FILES)

        return res

    @allure.step
    def get_file_upload_url(self, project_id, team_id, file_name):
        headers = {
            'accept': 'application/json, text/plain, */*',
            'content-type': 'application/json'
        }
        res = self.service.get(f"{FILE_UPLOAD_URL}"
                               f"?projectId={project_id}"
                               f"&teamId={team_id}"
                               f"&fileName={file_name}",
                               cookies=self.cookies,
                               headers=headers,
                               ep_name=FILE_UPLOAD_URL)

        return res

    @allure.step
    def get_list_of_downloaded_files(self, project_id, team_id, data_type):
        res = self.service.get(f"{FILE_DOWNLOAD_LIST}"
                               f"?projectId={project_id}"
                               f"&teamId={team_id}"
                               f"&type={data_type}",
                               cookies=self.cookies,
                               ep_name=FILE_DOWNLOAD_LIST)

        return res

    @allure.step
    def post_notify_file(self, team_id, publish, payload, ignore_warning=None):
        """
        Send upload result and publish the file.
        """
        headers = {
            'accept': 'application/json, text/plain, */*',
            'content-type': 'application/json'
        }
        if ignore_warning is None:
            _url = f"{FILE_NOTIFY}?teamId={team_id}&publish={publish}"
        else:
            _url = f"{FILE_NOTIFY}?teamId={team_id}&publish={publish}&ignoreWarning={ignore_warning}"

        res = self.service.post(_url,
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                headers=headers,
                                ep_name=FILE_NOTIFY)

        return res

    @allure.step
    def post_download_file(self, team_id, payload):
        res = self.service.post(f"{FILE_DOWNLOAD}"
                                f"?teamId={team_id}",
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=FILE_DOWNLOAD)

        return res

    @allure.step
    def delete_file(self, id, project_id, team_id, version):
        headers = {'accept': '*/*'}
        res = self.service.delete(f"{FILE}"
                                  f"?projectId={project_id}"
                                  f"&teamId={team_id}"
                                  f"&version={version}"
                                  f"&id={id}",
                                  headers=headers,
                                  cookies=self.cookies,
                                  ep_name=FILE_DOWNLOAD)

        return res

    @allure.step
    def get_file_link(self, project_id, team_id, path):
        res = self.service.get(f"{FILE_LINK}"
                               f"?projectId={project_id}"
                               f"&teamId={team_id}"
                               f"&path={path}",
                               cookies=self.cookies,
                               ep_name=FILE_LINK)

        return res

    # ------------------------------------------------------------------------------------------
    # ---------------- Unit controller --------------------------- -----------------------------
    # ------------------------------------------------------------------------------------------
    @allure.step
    def post_units(self, project_id, team_id, payload):
        # {"startRow":0,"endRow":29,"filterModel":{},"sortModel":[],"queryString":""}
        res = self.service.post(f"{UNITS}"
                                f"?projectId={project_id}"
                                f"&teamId={team_id}",
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=UNITS)

        return res

    @allure.step
    def post_segment_group_list(self, team_id, project_id, payload):
        res = self.service.post(f"{SEGMENT_GROUP_LIST}"
                                f"?projectId={project_id}"
                                f"&teamId={team_id}",
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=SEGMENT_GROUP_LIST)

        return res

    @allure.step
    def post_job_preview_v2(self, job_id, team_id):
        res = self.service.post(f"{JOB_PREVIEW_V2}"
                                f"?jobId={job_id}"
                                f"&teamId={team_id}",
                                cookies=self.cookies,
                                ep_name=JOB_PREVIEW_V2)
        return res

    @allure.step
    def post_launch_job_v2(self, job_id, team_id):
        res = self.service.post(f"{JOB_LAUNCH_V2}"
                                f"?teamId={team_id}"
                                f"&jobId={job_id}",
                                cookies=self.cookies,
                                ep_name=JOB_LAUNCH_V2)
        return res

    @allure.step
    def post_send_to_job(self, job_id, team_id, payload, ignore_conflict='false'):
        # {"projectId":"207dab45-00e0-42d9-9cb4-77e5688f3387","unitIds":["a46591ca-6062-4cdb-9ce7-a86600e6e814"],"percentage":100}
        # unitIds from post_units=>
        res = self.service.post(f"{UNITS_SEND_TO_JOB}"
                                f"?jobId={job_id}"
                                f"&ignoreConflict={ignore_conflict}"
                                f"&teamId={team_id}",
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=UNITS_SEND_TO_JOB)

        return res

    @allure.step
    def post_send_to_group(self, team_id, payload):
        # https://api-kepler.integration.cf3.us/project/send-to-group?teamId=5b0b9027-e6cd-45aa-b03f-f5b6e7b8541c
        # {"dataGroup":{"projectId":"207dab45-00e0-42d9-9cb4-77e5688f3387","name":"test1"},"units":{"projectId":"207dab45-00e0-42d9-9cb4-77e5688f3387","unitIds":["29fb7544-4955-4ef2-ae79-2ff791626278"]}}
        res = self.service.post(f"{UNITS_SEND_TO_GROUP}"
                                f"?teamId={team_id}",
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=UNITS_SEND_TO_GROUP)

        return res

    @allure.step
    def post_send_to_contributor(self, contributor_id, job_id, team_id, payload):
        # https://api-kepler.integration.cf3.us/project/send-to-contributor?contributorId=a5ef7e5a-8242-4c8d-82a4-880e04412ede&jobId=bae18488-7dc0-445b-b704-9bbe6fe340bf&teamId=5b0b9027-e6cd-45aa-b03f-f5b6e7b8541c
        # {"projectId":"207dab45-00e0-42d9-9cb4-77e5688f3387","filterModel":{},"queryString":""}  all units
        # {"projectId":"207dab45-00e0-42d9-9cb4-77e5688f3387","unitIds":["97e01301-e376-43a2-8e5b-8d621db15060"]}
        res = self.service.post(f"{UNITS_SEND_TO_CONTRIBUTOR}"
                                f"?jobId={job_id}"
                                f"&contributorId={contributor_id}"
                                f"&teamId={team_id}",
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=UNITS_SEND_TO_CONTRIBUTOR)

        return res

    @allure.step
    def post_remove_from_job(self, team_id, payload, ignore_conflict='false'):
        # https://api-kepler.integration.cf3.us/project/remove-from-job?ignoreConflict=true&teamId=5b0b9027-e6cd-45aa-b03f-f5b6e7b8541c
        # if ignoreConflict=false modal window, if true ignore ?
        # {"projectId":"207dab45-00e0-42d9-9cb4-77e5688f3387","unitIds":["c37ebe6f-29f5-4d48-91b8-522ec0bacd21"]}
        res = self.service.post(f"{UNITS_REMOVE_FROM_JOB}"
                                f"?ignoreConflict={ignore_conflict}"
                                f"&teamId={team_id}",
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=UNITS_REMOVE_FROM_JOB)

        return res

    @allure.step
    def post_remove_from_group(self, team_id, group_id, payload):
        # https://api-kepler.integration.cf3.us/project/remove-from-group?groupId=6396d947-c95e-4e7d-8ed8-ead279d79c0b&teamId=5b0b9027-e6cd-45aa-b03f-f5b6e7b8541c
        # {"projectId":"207dab45-00e0-42d9-9cb4-77e5688f3387","filterModel":{},"queryString":""}
        res = self.service.post(f"{UNITS_REMOVE_FROM_GROUP}"
                                f"?groupId={group_id}"
                                f"&teamId={team_id}",
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=UNITS_REMOVE_FROM_GROUP)

        return res

    @allure.step
    def post_remove_from_contributor(self, team_id, job_id, payload):
        res = self.service.post(f"{UNITS_REMOVE_FROM_CONTRIBUTOR}"
                                f"?teamId={team_id}"
                                f"&jobId={job_id}",
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=UNITS_REMOVE_FROM_CONTRIBUTOR)

        return res

    @allure.step
    def post_recover_units(self, team_id, payload):
        # https://api-kepler.integration.cf3.us/project/recover-units?teamId=5b0b9027-e6cd-45aa-b03f-f5b6e7b8541c
        # {"projectId":"207dab45-00e0-42d9-9cb4-77e5688f3387","filterModel":{},"queryString":""}
        res = self.service.post(f"{UNITS_RECOVER}"
                                f"?teamId={team_id}",
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=UNITS_RECOVER)

        return res

    @allure.step
    def post_inactive_units(self, team_id, project_id, payload):
        # https://api-kepler.integration.cf3.us/project/inactive-units?projectId=207dab45-00e0-42d9-9cb4-77e5688f3387&teamId=5b0b9027-e6cd-45aa-b03f-f5b6e7b8541c
        # {"startRow": 0, "endRow": 29, "filterModel": {}, "sortModel": [], "queryString": ""}
        res = self.service.post(f"{UNITS_INACTIVE}"
                                f"?teamId={team_id}"
                                f"&projectId={project_id}",
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=UNITS_INACTIVE)

        return res

    @allure.step
    def post_field_values(self, team_id, project_id, payload):
        # upload data
        # https://api-kepler.integration.cf3.us/project/field-values?projectId=73f787ac-7b5c-4189-8aee-855e8405d06b&teamId=f8fb3aaf-f3f1-437a-9bb8-170c136e9084
        res = self.service.post(f"{FIELD_VALUES}"
                                f"?teamId={team_id}"
                                f"&projectId={project_id}",
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=FIELD_VALUES)

        return res

    @allure.step
    def post_delete_units(self, team_id, payload, ignore_jobs='false'):
        # https://api-kepler.integration.cf3.us/project/delete-units?ignoreJobs=false&teamId=5b0b9027-e6cd-45aa-b03f-f5b6e7b8541c
        # ["jobStatus"]
        # {"projectId": "207dab45-00e0-42d9-9cb4-77e5688f3387", "unitIds": ["c37ebe6f-29f5-4d48-91b8-522ec0bacd21"]}
        res = self.service.post(f"{UNITS_DELETE}"
                                f"?teamId={team_id}"
                                f"&ignoreJobs={ignore_jobs}",
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=UNITS_DELETE)

        return res

    @allure.step
    def post_data_group_list(self, team_id, project_id, payload):
        # https://api-kepler.integration.cf3.us/project/data-group-list?projectId=207dab45-00e0-42d9-9cb4-77e5688f3387&teamId=5b0b9027-e6cd-45aa-b03f-f5b6e7b8541c
        # {} payload
        res = self.service.post(f"{UNITS_DATA_GROUP_LIST}"
                                f"?teamId={team_id}"
                                f"&projectId={project_id}",
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=UNIT_DATA_GROUP)

        return res

    @allure.step
    def delete_data_group(self, team_id, project_id, group_id):
        res = self.service.delete(f"{UNIT_DATA_GROUP}"
                                  f"?teamId={team_id}"
                                  f"&projectId={project_id}"
                                  f"&groupId={group_id}",
                                  cookies=self.cookies,
                                  ep_name=UNIT_DATA_GROUP)

        return res

    @allure.step
    def get_units_header(self, team_id, project_id):
        res = self.service.get(f"{UNITS_HEADER}"
                               f"?teamId={team_id}"
                               f"&projectId={project_id}",
                               cookies=self.cookies,
                               ep_name=UNITS_HEADER)

        return res

    @allure.step
    def get_unit(self, team_id, project_id, unit_id):
        res = self.service.get(f"{UNIT}"
                               f"?teamId={team_id}"
                               f"&projectId={project_id}"
                               f"&unitId={unit_id}",
                               cookies=self.cookies,
                               ep_name=UNIT)

        return res

    @allure.step
    def get_unit_commit_history(self, team_id, project_id, unit_segment_id):
        # https://api-kepler.integration.cf3.us/project/unit-commit-history?unitSegmentId=c37ebe6f-29f5-4d48-91b8-522ec0bacd21&projectId=207dab45-00e0-42d9-9cb4-77e5688f3387&teamId=5b0b9027-e6cd-45aa-b03f-f5b6e7b8541c
        res = self.service.get(f"{UNIT_COMMIT_HISTORY}"
                               f"?teamId={team_id}"
                               f"&projectId={project_id}"
                               f"&unitSegmentId={unit_segment_id}",
                               cookies=self.cookies,
                               ep_name=UNIT_COMMIT_HISTORY)

        return res

    @allure.step
    def delete_group(self, team_id, project_id, group_id):
        # https://api-kepler.integration.cf3.us/project/data-group?projectId=207dab45-00e0-42d9-9cb4-77e5688f3387&groupId=6396d947-c95e-4e7d-8ed8-ead279d79c0b&teamId=5b0b9027-e6cd-45aa-b03f-f5b6e7b8541c
        res = self.service.delete(f"{UNITS_DELETE}"
                                  f"?teamId={team_id}"
                                  f"&projectId={project_id}"
                                  f"&groupId={group_id}",
                                  cookies=self.cookies,
                                  ep_name=UNITS_DELETE)

        return res

    # ------------------------------------------------------------------------------------------
    # ---------------- Feedback controller --------------------------- -------------------------
    # ------------------------------------------------------------------------------------------
    @allure.step
    def get_feedback_statistics(self, team_id, project_id):
        headers = {'accept': '*/*'}
        # https://api-kepler.integration.cf3.us/project/feedback/statistics?projectId=c87f67ec-8618-4644-8ab8-8f97d8073c94&teamId=f8fb3aaf-f3f1-437a-9bb8-170c136e9084
        res = self.service.get(f"{FEEDBACK_STATISTICS}"
                               f"?teamId={team_id}"
                               f"&projectId={project_id}",
                               headers=headers,
                               cookies=self.cookies,
                               ep_name=FEEDBACK_STATISTICS)
        return res

    @allure.step
    def get_feedback_columns(self, team_id, project_id):
        # https://api-kepler.integration.cf3.us/project/feedback/columns?projectId=c87f67ec-8618-4644-8ab8-8f97d8073c94&teamId=f8fb3aaf-f3f1-437a-9bb8-170c136e9084
        res = self.service.get(f"{FEEDBACK_COLUMNS}"
                               f"?teamId={team_id}"
                               f"&projectId={project_id}",
                               cookies=self.cookies,
                               ep_name=FEEDBACK_COLUMNS)
        return res

    @allure.step
    def post_feedback_list(self, team_id, project_id, payload):
        # https://api-kepler.integration.cf3.us/project/feedback/list?teamId=f8fb3aaf-f3f1-437a-9bb8-170c136e9084&projectId=c87f67ec-8618-4644-8ab8-8f97d8073c94
        # {"startRow":0,"endRow":0,"filterModel":{},"sortModel":[],"queryString":""}
        res = self.service.post(f"{FEEDBACK_LIST}"
                                f"?teamId={team_id}"
                                f"&projectId={project_id}",
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=FEEDBACK_LIST)
        return res

    @allure.step
    def post_list_of_invoices(self, team_id, project_id, payload):
        res = self.service.post(f"{INVOICE_LIST}"
                                f"?teamId={team_id}"
                                f"&projectId={project_id}",
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=INVOICE_LIST
                                )
        return res

    @allure.step
    def post_retry_of_invoices(self, team_id, project_id, payload):
        res = self.service.post(f"{INVOICE_RETRY}"
                                f"?teamId={team_id}"
                                f"&projectId={project_id}",
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=INVOICE_RETRY)
        return res

    @allure.step
    def post_trigger_invoices(self, batchjobId):
        res = self.service.post(f"{BATCH_JOB_TRIGGER}"
                                f"?batchjobId={batchjobId}",
                                cookies=self.cookies,
                                ep_name=BATCH_JOB_TRIGGER)
        return res


class QualityFlowApiBatchjob(QualityFlowApi):
    # ------------------------------------------------------------------------------------------
    # ----------------Batchjob Progress Controller--------------------------- -----------------------------
    # ------------------------------------------------------------------------------------------
    @allure.step
    def post_batch_progress_list(self, team_id, project_id, payload):
        res = self.service.post(f"{BATCH_PROGRESS_LIST}"
                                f"?teamId={team_id}"
                                f"&projectId={project_id}",
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=BATCH_PROGRESS_LIST)
        return res

    @allure.step
    def post_batch_progress_history(self, team_id, project_id, batchjobId, payload):
        res = self.service.post(f"{BATCH_PROGRESS_HISTORY}"
                                f"?teamId={team_id}"
                                f"&projectId={project_id}"
                                f"&batchjobId={batchjobId}",
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=BATCH_PROGRESS_HISTORY)
        return res


class QualityFlowApiContributor(QualityFlowApi):
    """
    https://api-kepler.integration.cf3.us/contributor/swagger-ui/index.html#/
    """

    def __init__(self, custom_url=None, payload=None, env=None, api_key=None, session=None):
        super().__init__(custom_url=custom_url, payload=payload, env=env, api_key=api_key, session=session)

    # ------------------------------------------------------------------------------------------
    # ---------------- Curated Crowd sync-setting-manage-controller ----------------------------
    # ------------------------------------------------------------------------------------------
    def put_contributor_sync_setting_update(self, team_id, payload):
        res = self.service.put(f"{CONTRIBUTOR_SYNC_SETTING_UPDATE}"
                               f"?teamId={team_id}",
                               data=json.dumps(payload),
                               cookies=self.cookies,
                               ep_name=CONTRIBUTOR_SYNC_SETTING_UPDATE)

        return res

    def put_contributor_sync_setting_effect(self, project_id, team_id):
        res = self.service.put(f"{CONTRIBUTOR_SYNC_SETTING_EFFECT}"
                               f"?projectId={project_id}"
                               f"&teamId={team_id}",
                               cookies=self.cookies,
                               ep_name=CONTRIBUTOR_SYNC_SETTING_EFFECT)

        return res

    def post_contributor_sync_setting_refresh(self, project_id, team_id, setting_id):
        res = self.service.post(f"{CONTRIBUTOR_SYNC_SETTING_REFRESH}"
                                f"?projectId={project_id}"
                                f"&teamId={team_id}"
                                f"&settingId={setting_id}",
                                cookies=self.cookies,
                                ep_name=CONTRIBUTOR_SYNC_SETTING_REFRESH)

        return res

    def post_contributor_sync_setting_create(self, team_id, payload):
        res = self.service.post(f"{CONTRIBUTOR_SYNC_SETTING_CREATE}"
                                f"?teamId={team_id}",
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=CONTRIBUTOR_SYNC_SETTING_CREATE)

        return res

    def patch_contributor_sync_setting_update_external_project(self, team_id, payload):
        res = self.service.patch(f"{CONTRIBUTOR_SYNC_SETTING_UPDATE_EXTERNAL_PROJECT}"
                                 f"?teamId={team_id}",
                                 data=json.dumps(payload),
                                 cookies=self.cookies,
                                 ep_name=CONTRIBUTOR_SYNC_SETTING_UPDATE_EXTERNAL_PROJECT)

        return res

    def post_contributor_sync_setting_job_link(self, team_id, payload):
        res = self.service.post(f"{CONTRIBUTOR_SYNC_SETTING_JOB_LINK}"
                                f"?teamId={team_id}",
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=CONTRIBUTOR_SYNC_SETTING_JOB_LINK)

        return res

    def post_contributor_sync_setting_create_effect(self, team_id, payload):
        res = self.service.post(f"{CONTRIBUTOR_SYNC_SETTING_CREATE_EFFECT}"
                                f"?teamId={team_id}",
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=CONTRIBUTOR_SYNC_SETTING_CREATE_EFFECT)

        return res

    @allure.step
    def get_contributor_sync_setting_external_project_check(self, team_id, external_project_id,
                                                            external_source="APPEN_CONNECT"):
        res = self.service.get(f"{CONTRIBUTOR_SYNC_SETTING_EXTERNAL_PROJECT_CHECK}"
                               f"?teamId={team_id}"
                               f"&externalProjectId={external_project_id}"
                               f"&externalSource={external_source}",
                               cookies=self.cookies,
                               ep_name=CONTRIBUTOR_SYNC_SETTING_EXTERNAL_PROJECT_CHECK)

        return res

    @allure.step
    def get_contributor_sync_setting_list(self, team_id, project_id, external_source="APPEN_CONNECT"):
        res = self.service.get(f"{CONTRIBUTOR_SYNC_SETTING_LIST}"
                               f"?teamId={team_id}"
                               f"&projectId={project_id}"
                               f"&externalSource={external_source}",
                               cookies=self.cookies,
                               ep_name=CONTRIBUTOR_SYNC_SETTING_LIST)

        return res

    @allure.step
    def get_contributor_sync_setting_detail_by_job(self, team_id, project_id, job_id):
        res = self.service.get(f"{CONTRIBUTOR_SYNC_SETTING_DETAIL_BY_JOB}"
                               f"?teamId={team_id}"
                               f"&projectId={project_id}"
                               f"&jobId={job_id}",
                               cookies=self.cookies,
                               ep_name=CONTRIBUTOR_SYNC_SETTING_DETAIL_BY_JOB)

        return res

    # ------------------------------------------------------------------------------------------
    # ---------------- Curated Crowd sync-setting-biz-controller ----------------------------
    # ------------------------------------------------------------------------------------------
    def put_contributor_sync_setting_update_effect(self, team_id, payload):
        res = self.service.put(f"{CONTRIBUTOR_SYNC_SETTING_UPDATE_EFFECT}"
                               f"?teamId={team_id}",
                               data=json.dumps(payload),
                               cookies=self.cookies,
                               ep_name=CONTRIBUTOR_SYNC_SETTING_UPDATE_EFFECT)

        return res

    # ------------------------------------------------------------------------------------------
    # ---------------- Curated Crowd sync-setting-query-controller ----------------------------
    # ------------------------------------------------------------------------------------------
    @allure.step
    def get_contributor_sync_setting_external_user_group(self, project_id, team_id, external_source="APPEN_CONNECT"):
        res = self.service.get(f"{CONTRIBUTOR_SYNC_SETTING_EXTERNAL_USER_GROUP}"
                               f"?projectId={project_id}"
                               f"&teamId={team_id}"
                               f"&externalSource={external_source}",
                               cookies=self.cookies,
                               ep_name=CONTRIBUTOR_SYNC_SETTING_EXTERNAL_USER_GROUP)

        return res

    @allure.step
    def get_contributor_sync_setting_external_locale(self, project_id, team_id, external_source="APPEN_CONNECT"):
        res = self.service.get(f"{CONTRIBUTOR_SYNC_SETTING_EXTERNAL_LOCALE}"
                               f"?projectId={project_id}"
                               f"&teamId={team_id}"
                               f"&externalSource={external_source}",
                               cookies=self.cookies,
                               ep_name=CONTRIBUTOR_SYNC_SETTING_EXTERNAL_LOCALE)

        return res

    @allure.step
    def get_contributor_sync_setting_detail(self, team_id, setting_id=None):
        res = self.service.get(f"{CONTRIBUTOR_SYNC_SETTING_DETAIL}"
                               f"?teamId={team_id}"
                               f"&settingId={setting_id}",
                               cookies=self.cookies,
                               ep_name=CONTRIBUTOR_SYNC_SETTING_DETAIL)

        return res

    @allure.step
    def get_contributor_sync_setting_pay_rate_list(self, project_id, team_id, job_id):
        res = self.service.get(f"{CONTRIBUTOR_SYNC_SETTING_PAY_RATE_LIST}"
                               f"?projectId={project_id}"
                               f"&teamId={team_id}"
                               f"&jobId={job_id}",
                               cookies=self.cookies,
                               ep_name=CONTRIBUTOR_SYNC_SETTING_PAY_RATE_LIST)

        return res

    # ------------------------------------------------------------------------------------------
    # ---------------- Curated Crowd contributor-manage-controller -----------------------------
    # ------------------------------------------------------------------------------------------
    def post_contributor_crowd_un_assign_job(self, team_id, payload):
        res = self.service.post(f"{CONTRIBUTOR_CROWD_UN_ASSIGN_JOB}"
                                f"?teamId={team_id}",
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=CONTRIBUTOR_CROWD_UN_ASSIGN_JOB)

        return res

    def post_contributor_crowd_clone(self, team_id, payload):
        res = self.service.post(f"{CONTRIBUTOR_CROWD_CLONE}"
                                f"?teamId={team_id}",
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=CONTRIBUTOR_CROWD_CLONE)

        return res

    def post_contributor_crowd_assign_job(self, team_id, payload):
        res = self.service.post(f"{CONTRIBUTOR_CROWD_ASSIGN_JOB}"
                                f"?teamId={team_id}",
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=CONTRIBUTOR_CROWD_ASSIGN_JOB)

        return res

    # ------------------------------------------------------------------------------------------
    # ---------------- Curated Crowd contributor-query-controller ------------------------------
    # ------------------------------------------------------------------------------------------
    @allure.step
    def post_contributor_crowd_list_by_criteria_search(self, team_id, payload):
        res = self.service.post(f"{CONTRIBUTOR_CROWD_LIST_BY_CRITERIA_SEARCH}"
                                f"?teamId={team_id}",
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=CONTRIBUTOR_CROWD_LIST_BY_CRITERIA_SEARCH)

        return res

    @allure.step
    def post_contributor_crowd_criteria_search(self, team_id, payload):
        res = self.service.post(f"{CONTRIBUTOR_CROWD_CRITERIA_SEARCH}"
                                f"?teamId={team_id}",
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=CONTRIBUTOR_CROWD_CRITERIA_SEARCH)

        return res

    @allure.step
    def post_contributor_crowd_batch_detail(self, team_id, payload):
        res = self.service.post(f"{CONTRIBUTOR_CROWD_BATCH_DETAIL}"
                                f"?teamId={team_id}",
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=CONTRIBUTOR_CROWD_BATCH_DETAIL)

        return res

    @allure.step
    def get_contributor_crowd_list_by_group(self, project_id, team_id, group_id):
        res = self.service.get(f"{CONTRIBUTOR_CROWD_LIST_BY_GROUP}"
                               f"?projectId={project_id}"
                               f"&teamId={team_id}"
                               f"&groupId={group_id}",
                               cookies=self.cookies,
                               ep_name=CONTRIBUTOR_CROWD_LIST_BY_GROUP)

        return res

    # ------------------------------------------------------------------------------------------
    # ---------------- Curated Crowd crowd-group-manage-controller -----------------------------
    # ------------------------------------------------------------------------------------------
    @allure.step
    def put_contributor_crowd_group_update(self, team_id, payload):
        res = self.service.put(f"{CONTRIBUTOR_CROWD_GROUP_UPDATE}"
                               f"?teamId={team_id}",
                               data=json.dumps(payload),
                               cookies=self.cookies,
                               ep_name=CONTRIBUTOR_CROWD_GROUP_UPDATE)

        return res

    @allure.step
    def post_contributor_crowd_group_unlink_job(self, team_id, payload):
        res = self.service.post(f"{CONTRIBUTOR_CROWD_GROUP_UNLINK_JOB}"
                                f"?teamId={team_id}",
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=CONTRIBUTOR_CROWD_GROUP_UNLINK_JOB)

        return res

    @allure.step
    def post_contributor_crowd_group_remove_crowd(self, team_id, payload):
        res = self.service.post(f"{CONTRIBUTOR_CROWD_GROUP_REMOVE_CROWD}"
                                f"?teamId={team_id}",
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=CONTRIBUTOR_CROWD_GROUP_REMOVE_CROWD)

        return res

    @allure.step
    def post_contributor_crowd_group_link_job(self, team_id, payload):
        res = self.service.post(f"{CONTRIBUTOR_CROWD_GROUP_LINK_JOB}"
                                f"?teamId={team_id}",
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=CONTRIBUTOR_CROWD_GROUP_LINK_JOB)

        return res

    @allure.step
    def post_contributor_crowd_group_create(self, team_id, payload):
        res = self.service.post(f"{CONTRIBUTOR_CROWD_GROUP_CREATE}"
                                f"?teamId={team_id}",
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=CONTRIBUTOR_CROWD_GROUP_CREATE)

        return res

    @allure.step
    def post_contributor_crowd_group_create_with_crowd(self, team_id, payload):
        res = self.service.post(f"{CONTRIBUTOR_CROWD_GROUP_CREATE_WITH_CROWD}"
                                f"?teamId={team_id}",
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=CONTRIBUTOR_CROWD_GROUP_CREATE_WITH_CROWD)

        return res

    @allure.step
    def post_contributor_crowd_group_create_with_criteria(self, team_id, payload):
        res = self.service.post(f"{CONTRIBUTOR_CROWD_GROUP_CREATE_WITH_CRITERIA}"
                                f"?teamId={team_id}",
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=CONTRIBUTOR_CROWD_GROUP_CREATE_WITH_CRITERIA)

        return res

    @allure.step
    def post_contributor_crowd_group_add_crowd(self, team_id, payload):
        res = self.service.post(f"{CONTRIBUTOR_CROWD_GROUP_ADD_CROWD}"
                                f"?teamId={team_id}",
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=CONTRIBUTOR_CROWD_GROUP_ADD_CROWD)

        return res

    @allure.step
    def delete_contributor_crowd_group_delete(self, project_id, group_id, team_id):
        res = self.service.delete(f"{CONTRIBUTOR_CROWD_GROUP_DELETE}"
                                  f"?groupId={group_id}"
                                  f"&projectId={project_id}"
                                  f"&teamId={team_id}",
                                  cookies=self.cookies,
                                  ep_name=CONTRIBUTOR_CROWD_GROUP_DELETE)

        return res

    # ------------------------------------------------------------------------------------------
    # ---------------- Curated Crowd crowd-group-query-controller ------------------------------
    # ------------------------------------------------------------------------------------------
    @allure.step
    def post_contributor_crowd_group_detail_list(self, team_id, payload):
        res = self.service.post(f"{CONTRIBUTOR_CROWD_GROUP_DETAIL_LIST}"
                                f"?teamId={team_id}",
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=CONTRIBUTOR_CROWD_GROUP_DETAIL_LIST)

        return res

    @allure.step
    def get_contributor_crowd_group_brief_list(self, project_id, team_id, setting_id):
        res = self.service.get(f"{CONTRIBUTOR_CROWD_GROUP_BRIEF_LIST}"
                               f"?projectId={project_id}"
                               f"&teamId={team_id}"
                               f"&settingId={setting_id}",
                               cookies=self.cookies,
                               ep_name=CONTRIBUTOR_CROWD_GROUP_BRIEF_LIST)

        return res

    # ------------------------------------------------------------------------------------------
    # ---------------- Curated Crowd crowd-group-biz-controller --------------------------------
    # ------------------------------------------------------------------------------------------
    @allure.step
    def post_contributor_crowd_group_create_with_condition(self, team_id, payload):
        res = self.service.post(f"{CONTRIBUTOR_CROWD_GROUP_CREATE_WITH_CONDITION}"
                                f"?teamId={team_id}",
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=CONTRIBUTOR_CROWD_GROUP_CREATE_WITH_CONDITION)

        return res

    # ------------------------------------------------------------------------------------------
    # ------------------------------- Curated Crowd internal -----------------------------------
    # ------------------------------------------------------------------------------------------
    @allure.step
    def post_contributor_test_create_contributor(self, project_id, number, team_id):
        original_url, self.service.base_url = self.service.base_url, self.kepler_internal_api_gateway_url
        res = self.service.post(f"{CONTRIBUTOR_TEST_CREATE_CONTRIBUTOR}"
                                f"?projectId={project_id}"
                                f"&number={number}"
                                f"&teamId={team_id}",
                                cookies=self.cookies,
                                ep_name=CONTRIBUTOR_TEST_CREATE_CONTRIBUTOR)
        self.service.base_url = original_url
        return res

    # ------------------------------------------------------------------------------------------
    # ---------------------------- Internal Contributor ----------------------------------------
    # ------------------------------------------------------------------------------------------

    @allure.step
    def post_internal_contributor_create(self, email, name, team_id):
        payload = json.dumps({
            "email": email,
            "name": name
        })
        params = {"teamId": team_id}

        res = self.service.post(f"{CONTRIBUTOR_INTERNAL_ADD_CONTRIBUTOR}", cookies=self.cookies, params=params,
                                data=payload)
        return res

    @allure.step
    def post_internal_contributor_group_create(self, group_name, description):
        payload = json.dumps({
            "name": group_name,
            "description": description
        })

        res = self.service.post(f"{CONTRIBUTOR_INTERNAL_ADD_GROUP}", cookies=self.cookies, data=payload)

        return res

    @allure.step
    def post_add_multiple_contributors_to_new_group(self, group_name, contributor_ids, team_id):
        payload = json.dumps({
            "name": group_name,
            "contributorIds": contributor_ids
        })
        params = {"teamId": team_id}

        res = self.service.post(f"{CONTRIBUTOR_INTERNAL_ADD_CONTRIBUTOR_TO_NEW_GROUP}", cookies=self.cookies,
                                params=params, data=payload)

        return res

    @allure.step
    def post_search_contributor_by_name(self, name, team_id):
        payload = json.dumps({
            "queryString": name,
            "pageNumber": 1,
            "pageSize": 10,
            "sortModel": [
                {"colId": "name",
                 "sort": "asc"}
            ]
        })
        params = {"teamId": team_id}

        res = self.service.post(f"{CONTRIBUTOR_INTERNAL_LIST_CONTRIBUTOR}", cookies=self.cookies, params=params,
                                data=payload)

        return res

    @allure.step
    def post_add_multiple_contributors_to_new_group(self, group_name, contributor_ids, team_id):
        payload = json.dumps({
            "name": group_name,
            "contributorIds": contributor_ids
        })
        params = {"teamId": team_id}

        res = self.service.post(f"{CONTRIBUTOR_INTERNAL_ADD_CONTRIBUTOR_TO_NEW_GROUP}", cookies=self.cookies,
                                params=params, data=payload)

        return res

    def post_internal_contributor_list(self, group_name, description, team_id):
        payload = json.dumps({
            "name": group_name,
            "description": description
        })
        params = {"teamId": team_id}

        res = self.service.post(f"{CONTRIBUTOR_INTERNAL_ADD_GROUP}", cookies=self.cookies, params=params, data=payload)

        return res

    def post_assign_contributor_group_to_job(self, project_id, job_id, group_ids, team_id):
        payload = json.dumps({
            "projectId": project_id,
            "jobId": job_id,
            "groupIds": group_ids
        })
        params = {"teamId": team_id}

        res = self.service.post(f"{CONTRIBUTOR_INTERNAL_ASSIGN_GROUP_TO_JOB}", cookies=self.cookies, params=params,
                                data=payload)

        return res

    def post_assign_contributor_to_job(self, project_id, job_id, contributor_ids, team_id):
        payload = json.dumps({
            "projectId": project_id,
            "jobId": job_id,
            "contributorIds": contributor_ids
        })
        params = {"teamId": team_id}

        res = self.service.post(f"{CONTRIBUTOR_INTERNAL_ASSIGN_CONTRIBUTOR_TO_JOB}", cookies=self.cookies,
                                params=params,
                                data=payload)

        return res


class QualityFlowApiWork(QualityFlowApi):
    """
    https://api-kepler.sandbox.cf3.us/work/swagger-ui/index.html#/
    """

    def __init__(self, custom_url=None, payload=None, env=None, api_key=None, session=None):
        super().__init__(custom_url=custom_url, payload=payload, env=env, api_key=api_key, session=session)

    @allure.step
    def post_create_job(self, team_id, payload):
        res = self.service.post(f"{JOB}"
                                f"?teamId={team_id}",
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=JOB)

        return res

    @allure.step
    def post_create_job_v2(self, team_id, payload):
        res = self.service.post(f"{JOB_V2}"
                                f"?teamId={team_id}",
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=JOB_V2)

        return res

    @allure.step
    def post_create_dc_job_v2(self, team_id, payload):
        res = self.service.post(f"{DC_JOB_V2}"
                                f"?teamId={team_id}",
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=DC_JOB_V2)

        return res

    @allure.step
    def post_delete_job_v2(self, team_id, project_id, job_id):
        res = self.service.delete(f"{JOB_DELETE_V2}"
                                  f"?teamId={team_id}&projectId={project_id}&jobId={job_id}",
                                  cookies=self.cookies,
                                  ep_name=JOB_DELETE_V2)
        return res

    @allure.step
    def put_update_job(self, team_id, payload):
        res = self.service.put(f"{JOB}"
                               f"?teamId={team_id}",
                               data=json.dumps(payload),
                               cookies=self.cookies,
                               ep_name=JOB)
        return res

    @allure.step
    def put_update_job_v2(self, team_id, payload):
        res = self.service.put(f"{JOB_V2}"
                               f"?teamId={team_id}",
                               data=json.dumps(payload),
                               cookies=self.cookies,
                               ep_name=JOB_V2)
        return res

    @allure.step
    def put_launch_job(self, team_id, job_id, version):
        res = self.service.put(f"{JOB_LAUNCH}"
                               f"?teamId={team_id}"
                               f"&jobId={job_id}"
                               f"&version={version}",
                               cookies=self.cookies,
                               ep_name=JOB_LAUNCH)
        return res

    @allure.step
    def post_launch_job_v2(self, team_id, job_id):
        res = self.service.post(f"{JOB_LAUNCH_V2}"
                                f"?teamId={team_id}"
                                f"&jobId={job_id}",
                                cookies=self.cookies,
                                ep_name=JOB_LAUNCH_V2)
        return res

    @allure.step
    def get_job_launch_config(self, team_id, job_id):
        res = self.service.get(f"{JOB_LAUNCH_CONFIG}"
                               f"?teamId={team_id}"
                               f"&jobId={job_id}",
                               cookies=self.cookies,
                               ep_name=JOB_LAUNCH_CONFIG)
        return res

    @allure.step
    def post_job_launch_config(self, team_id, payload):
        res = self.service.post(f"{JOB_LAUNCH_CONFIG}"
                                f"?teamId={team_id}",
                                cookies=self.cookies,
                                data=json.dumps(payload),
                                ep_name=JOB_LAUNCH_CONFIG)
        return res

    @allure.step
    def post_clone_job(self, team_id, payload):
        res = self.service.post(f"{JOB_CLONE}"
                                f"?teamId={team_id}",
                                cookies=self.cookies,
                                data=json.dumps(payload),
                                ep_name=JOB_CLONE)
        return res

    @allure.step
    def post_clone_job_v2(self, team_id, payload):
        res = self.service.post(f"{JOB_CLONE_V2}"
                                f"?teamId={team_id}",
                                cookies=self.cookies,
                                data=json.dumps(payload),
                                ep_name=JOB_CLONE_V2)
        return res

    @allure.step
    def get_job_summary(self, team_id, project_id, job_id):
        res = self.service.get(f"{JOB_SUMMARY}"
                               f"?teamId={team_id}"
                               f"&jobId={job_id}"
                               f"&projectId={project_id}",
                               cookies=self.cookies,
                               ep_name=JOB_SUMMARY)

        return res

    @allure.step
    def get_job_list_as_flow(self, team_id, project_id, order_by=None, descending=None):
        res = self.service.get(f"{JOB_LIST_AS_FLOW}"
                               f"?teamId={team_id}"
                               f"&projectId={project_id}",
                               cookies=self.cookies,
                               ep_name=JOB_LIST_AS_FLOW)

        return res

    @allure.step
    def get_job_with_cml(self, team_id, id):
        headers = {'accept': '*/*'}
        res = self.service.get(f"{JOB_WITH_CML}"
                               f"?id={id}"
                               f"&teamId={team_id}",
                               cookies=self.cookies,
                               headers=headers,
                               ep_name=JOB_WITH_CML)

        return res

    @allure.step
    def get_job_by(self, team_id, id):
        res = self.service.get(f"{JOB_BY}"
                               f"?teamId={team_id}"
                               f"&id={id}",
                               cookies=self.cookies,
                               ep_name=JOB_BY)

        return res

    @allure.step
    def get_job_appendable_as_collection(self, team_id, project_id):
        res = self.service.get(f"{JOB_COLLECTION}"
                               f"?teamId={team_id}"
                               f"&projectId={project_id}",
                               cookies=self.cookies,
                               ep_name=JOB_COLLECTION)

        return res

    @allure.step
    def get_job_all(self,
                    team_id,
                    project_id,
                    page_num=0,
                    page_size=20,
                    order_by='createdAt',
                    descending='true',
                    criteria=None):

        _url = f"{JOB_ALL}" \
               f"?teamId={team_id}" \
               f"&projectId={project_id}" \
               f"&pageNum={page_num}" \
               f"&orderBy={order_by}" \
               f"&descending={descending}" \
               f"&pageSize={page_size}"

        if criteria: _url += f"&criteria={criteria}"

        res = self.service.get(_url,
                               cookies=self.cookies,
                               ep_name=JOB_ALL)

        return res

    @allure.step
    def get_job_all_as_collection(self,
                                  team_id,
                                  project_id,
                                  criteria=None,
                                  cycle_num=None):

        _url = f"{JOB_ALL_COLLECTION}" \
               f"?teamId={team_id}" \
               f"&projectId={project_id}"

        if criteria: _url += f"&criteria={criteria}"
        if cycle_num: _url += f"&cycleNum={cycle_num}"

        res = self.service.get(_url,
                               cookies=self.cookies,
                               ep_name=JOB_ALL_COLLECTION)

        return res

    @allure.step
    def post_jobs_by_list_v2(self, team_id, project_id, payload):
        res = self.service.post(f"{JOBS_BY_LIST_V2}"
                                f"?teamId={team_id}"
                                f"&projectId={project_id}",
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=JOBS_BY_LIST_V2)

        return res

    @allure.step
    def get_jobs_by_list_tree_node_v2(self, team_id, project_id):
        res = self.service.get(f"{JOBS_BY_LIST_TREE_NODE_V2}"
                               f"?teamId={team_id}"
                               f"&projectId={project_id}",
                               cookies=self.cookies,
                               ep_name=JOBS_BY_LIST_TREE_NODE_V2)

        return res

    @allure.step
    def post_job_by_id_v2(self, team_id, job_id, payload):
        res = self.service.post(f"{JOB_BY_ID_V2}"
                                f"?teamId={team_id}"
                                f"&jobId={job_id}",
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=JOB_BY_ID_V2)

        return res

    #   ----- job-cml-controller ----------------
    @allure.step
    def get_cml(self, team_id, job_id):
        res = self.service.get(f"{CML}"
                               f"?teamId={team_id}"
                               f"&jobId={job_id}",
                               cookies=self.cookies,
                               ep_name=CML)

        return res

    @allure.step
    def put_cml(self, team_id, payload):
        res = self.service.put(f"{CML}"
                               f"?teamId={team_id}",
                               cookies=self.cookies,
                               data=json.dumps(payload),
                               ep_name=CML)
        return res

    @allure.step
    def delete_cml(self, team_id, job_id):
        res = self.service.delete(f"{CML}"
                                  f"?teamId={team_id}"
                                  f"&jobId={job_id}",
                                  cookies=self.cookies,
                                  ep_name=CML)

        return res

    @allure.step
    def post_cml_clone(self, team_id, job_id, copied_from):
        res = self.service.post(f"{CML_CLONE}"
                                f"?teamId={team_id}"
                                f"&jobId={job_id}"
                                f"&copiedFrom={copied_from}",
                                cookies=self.cookies,
                                ep_name=CML_CLONE)
        return res

    # -------  job-resource-controller -----
    @allure.step
    def get_resource(self, team_id, job_id, resource_type):
        res = self.service.get(f"{RESOURCE}"
                               f"?teamId={team_id}"
                               f"&job_id={job_id}"
                               f"&resource_type={resource_type}",
                               cookies=self.cookies,
                               ep_name=RESOURCE)
        return res

    @allure.step
    def post_resource(self, team_id, job_id, resource_type, payload):
        res = self.service.post(f"{RESOURCE}"
                                f"?teamId={team_id}"
                                f"&job_id={job_id}"
                                f"&resource_type={resource_type}",
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=RESOURCE)
        return res

    @allure.step
    def delete_resource(self, team_id, job_id, resource_type):
        res = self.service.delete(f"{RESOURCE}"
                                  f"?teamId={team_id}"
                                  f"&job_id={job_id}"
                                  f"&resource_type={resource_type}",
                                  cookies=self.cookies,
                                  ep_name=RESOURCE)
        return res

    @allure.step
    def get_resource_data(self, team_id, job_id, resource_type):
        res = self.service.get(f"{RESOURCE_DATA}"
                               f"?teamId={team_id}"
                               f"&job_id={job_id}"
                               f"&resource_type={resource_type}",
                               cookies=self.cookies,
                               ep_name=RESOURCE_DATA)
        return res

    # -------  job-filter-controller -----
    @allure.step
    def get_job_filter(self):
        """
        endpoint is not used
        """
        pass

    @allure.step
    def post_job_filter(self):
        """
        endpoint is not used
        """
        pass

    @allure.step
    def put_job_filter(self):
        """
        endpoint is not used
        """
        pass

    @allure.step
    def post_job_filter_clone(self, team_id, copied_from, append_to, applied_to):
        res = self.service.post(f"{JOB_FILTER_CLONE}"
                                f"?teamId={team_id}"
                                f"&copiedFrom={copied_from}"
                                f"&appendTo={append_to}"
                                f"&appliedTo={applied_to}",
                                cookies=self.cookies,
                                ep_name=JOB_FILTER_CLONE)
        return res

    @allure.step
    def post_job_preview_v2(self, team_id, job_id):
        res = self.service.post(f"{JOB_PREVIEW_V2}"
                                f"?teamId={team_id}"
                                f"&jobId={job_id}",
                                cookies=self.cookies,
                                ep_name=JOB_PREVIEW_V2)
        return res

    @allure.step
    def post_job_resume_v2(self, team_id, job_id):
        res = self.service.post(f"{JOB_RESUME_V2}"
                                f"?teamId={team_id}"
                                f"&jobId={job_id}",
                                cookies=self.cookies,
                                ep_name=JOB_RESUME_V2)
        return res

    @allure.step
    def post_job_pause_v2(self, team_id, job_id):
        res = self.service.post(f"{JOB_PAUSE_V2}"
                                f"?teamId={team_id}"
                                f"&jobId={job_id}",
                                cookies=self.cookies,
                                ep_name=JOB_PAUSE_V2)
        return res

    @allure.step
    def get_dc_job_settings(self, job_id, team_id):
        res = self.service.get(f"{DC_JOB_SETTINGS}"
                               f"?jobId={job_id}"
                               f"&teamId={team_id}",
                               cookies=self.cookies,
                               ep_name=DC_JOB_SETTINGS)
        return res

    @allure.step
    def post_dc_job_settings(self, team_id, payload):
        res = self.service.post(f"{DC_JOB_SETTINGS}"
                                f"?teamId={team_id}",
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=DC_JOB_SETTINGS)
        return res

    @allure.step
    def post_dc_job_title_instruction(self, team_id, payload):
        res = self.service.post(f"{DC_JOB_UPDATE_TITLE_INSTRUCTION}"
                                f"?teamId={team_id}",
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=DC_JOB_UPDATE_TITLE_INSTRUCTION)
        return res

    @allure.step
    def put_dc_job_question(self, team_id, payload):
        res = self.service.put(f"{DC_JOB_QUESTION}"
                               f"?teamId={team_id}",
                               data=json.dumps(payload),
                               cookies=self.cookies,
                               ep_name=DC_JOB_QUESTION)
        return res

    @allure.step
    def post_dc_job_question(self, team_id, payload):
        res = self.service.post(f"{DC_JOB_QUESTION}"
                                f"?teamId={team_id}",
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=DC_JOB_QUESTION)
        return res

    @allure.step
    def post_dc_job_question_update_status(self, team_id, payload):
        res = self.service.post(f"{DC_JOB_QUESTION_UPDATE_STATUS}"
                                f"?teamId={team_id}",
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=DC_JOB_QUESTION_UPDATE_STATUS)
        return res

    @allure.step
    def post_dc_job_question_reorder(self, team_id, payload):
        res = self.service.post(f"{DC_JOB_QUESTION_REORDER}"
                                f"?teamId={team_id}",
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=DC_JOB_QUESTION_REORDER)
        return res

    @allure.step
    def post_dc_job_question_delete(self, team_id, payload):
        res = self.service.post(f"{DC_JOB_QUESTION_DELETE}"
                                f"?teamId={team_id}",
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=DC_JOB_QUESTION_DELETE)
        return res

    @allure.step
    def get_dc_job_question_simple_list(self, team_id, job_id):
        res = self.service.get(f"{DC_JOB_QUESTION_SIMPLE_LIST}"
                               f"?jobId={job_id}"
                               f"&teamId={team_id}",
                               cookies=self.cookies,
                               ep_name=DC_JOB_QUESTION_SIMPLE_LIST)
        return res

    @allure.step
    def get_dc_job_question_hidden_list(self, team_id, job_id):
        res = self.service.get(f"{DC_JOB_QUESTION_HIDDEN_LIST}"
                               f"?jobId={job_id}"
                               f"&teamId={team_id}",
                               cookies=self.cookies,
                               ep_name=DC_JOB_QUESTION_HIDDEN_LIST)
        return res

    @allure.step
    def get_dc_job_question_custom_list(self, job_id, team_id):
        res = self.service.get(f"{DC_JOB_QUESTION_CUSTOM_LIST}"
                               f"?jobId={job_id}"
                               f"&teamId={team_id}",
                               cookies=self.cookies,
                               ep_name=DC_JOB_QUESTION_CUSTOM_LIST)
        return res

    @allure.step
    def post_dc_pin_update_status(self, team_id, payload):
        res = self.service.post(f"{DC_PIN_UPDATE_STATUS}"
                                f"?teamId={team_id}",
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=DC_PIN_UPDATE_STATUS)
        return res

    @allure.step
    def post_dc_pin_list(self, team_id, payload):
        res = self.service.post(f"{DC_PIN_LIST}"
                                f"?teamId={team_id}",
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=DC_PIN_LIST)
        return res

    @allure.step
    def post_dc_pin_generate(self, team_id, payload):
        res = self.service.post(f"{DC_PIN_GENERATE}"
                                f"?teamId={team_id}",
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=DC_PIN_GENERATE)
        return res

    @allure.step
    def post_dc_pin_batch_update(self, team_id, payload):
        res = self.service.post(f"{DC_PIN_BATCH_UPDATE}"
                                f"?teamId={team_id}",
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=DC_PIN_BATCH_UPDATE)
        return res

    @allure.step
    def post_dc_pin_batch_count(self, team_id, payload):
        res = self.service.post(f"{DC_PIN_BATCH_COUNT}"
                                f"?teamId={team_id}",
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=DC_PIN_BATCH_COUNT)
        return res

    @allure.step
    def get_dc_pin_session_status_list(self, team_id):
        res = self.service.get(f"{DC_PIN_SESSION_STATUS_LIST}"
                               f"?teamId={team_id}",
                               cookies=self.cookies,
                               ep_name=DC_PIN_SESSION_STATUS_LIST)
        return res

    @allure.step
    def post_dc_prompt_send_to_group(self, team_id, payload):
        res = self.service.post(f"{DC_PROMPT_SEND_TO_GROUP}"
                                f"?teamId={team_id}",
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=DC_PROMPT_SEND_TO_GROUP)
        return res

    @allure.step
    def post_dc_prompt_out_to_group(self, team_id, payload):
        res = self.service.post(f"{DC_PROMPT_OUT_OF_GROUP}"
                                f"?teamId={team_id}",
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=DC_PROMPT_OUT_OF_GROUP)
        return res

    @allure.step
    def post_dc_prompt_group_reorder(self, team_id, payload):
        res = self.service.post(f"{DC_PROMPT_GROUP_REORDER}"
                                f"?teamId={team_id}",
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=DC_PROMPT_GROUP_REORDER)
        return res

    @allure.step
    def post_dc_prompt_group_release(self, team_id, payload):
        res = self.service.post(f"{DC_PROMPT_GROUP_RELEASE}"
                                f"?teamId={team_id}",
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=DC_PROMPT_GROUP_RELEASE)
        return res

    @allure.step
    def post_dc_prompt_group_prompt_shuffle(self, team_id, payload):
        res = self.service.post(f"{DC_PROMPT_GROUP_PROMPT_SHUFFLE}"
                                f"?teamId={team_id}",
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=DC_PROMPT_GROUP_PROMPT_SHUFFLE)
        return res

    @allure.step
    def post_dc_prompt_group_organize(self, team_id, payload):
        res = self.service.post(f"{DC_PROMPT_GROUP_ORGANIZE}"
                                f"?teamId={team_id}",
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=DC_PROMPT_GROUP_ORGANIZE)
        return res

    @allure.step
    def post_dc_prompt_group_edit(self, team_id, payload):
        res = self.service.post(f"{DC_PROMPT_GROUP_EDIT}"
                                f"?teamId={team_id}",
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=DC_PROMPT_GROUP_EDIT)
        return res

    @allure.step
    def post_dc_prompt_enable(self, team_id, payload):
        res = self.service.post(f"{DC_PROMPT_ENABLE}"
                                f"?teamId={team_id}",
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=DC_PROMPT_ENABLE)
        return res

    @allure.step
    def post_dc_prompt_element_reorder(self, team_id, payload):
        res = self.service.post(f"{DC_PROMPT_ELEMENT_REORDER}"
                                f"?teamId={team_id}",
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=DC_PROMPT_ELEMENT_REORDER)
        return res

    @allure.step
    def post_dc_prompt_element_list(self, team_id, payload):
        res = self.service.post(f"{DC_PROMPT_ELEMENT_LIST}"
                                f"?teamId={team_id}",
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=DC_PROMPT_ELEMENT_LIST)
        return res

    @allure.step
    def post_dc_prompt_edit(self, team_id, payload):
        res = self.service.post(f"{DC_PROMPT_EDIT}"
                                f"?teamId={team_id}",
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=DC_PROMPT_EDIT)
        return res

    @allure.step
    def post_dc_prompt_disable(self, team_id, payload):
        res = self.service.post(f"{DC_PROMPT_DISABLE}"
                                f"?teamId={team_id}",
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=DC_PROMPT_DISABLE)
        return res

    @allure.step
    def post_dc_prompt_delete(self, team_id, payload):
        res = self.service.post(f"{DC_PROMPT_DELETE}"
                                f"?teamId={team_id}",
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=DC_PROMPT_DELETE)
        return res

    @allure.step
    def post_dc_prompt_add(self, team_id, payload):
        res = self.service.post(f"{DC_PROMPT_ADD}"
                                f"?teamId={team_id}",
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=DC_PROMPT_ADD)

        return res

    def post_dc_interlocking_update_status(self, team_id, payload):
        res = self.service.post(f"{DC_INTERLOCKING_UPDATE_STATUS}"
                                f"?teamId={team_id}",
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=DC_INTERLOCKING_UPDATE_STATUS)
        return res

    @allure.step
    def post_dc_interlocking_update_quota(self, team_id, interlocking_id, target_quota):
        res = self.service.post(f"{DC_INTERLOCKING_UPDATE_QUOTA}"
                                f"?interlockingId={interlocking_id}"
                                f"&targetQuota={target_quota}"
                                f"&teamId={team_id}",
                                cookies=self.cookies,
                                ep_name=DC_INTERLOCKING_UPDATE_QUOTA)
        return res

    @allure.step
    def post_dc_interlocking_update_quota_config(self, team_id, payload):
        res = self.service.post(f"{DC_INTERLOCKING_UPDATE_QUOTA_CONFIG}"
                                f"?teamId={team_id}",
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=DC_INTERLOCKING_UPDATE_QUOTA_CONFIG)
        return res

    @allure.step
    def post_dc_interlocking_list(self, team_id, payload):
        res = self.service.post(f"{DC_INTERLOCKING_LIST}"
                                f"?teamId={team_id}",
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=DC_INTERLOCKING_LIST)
        return res

    @allure.step
    def post_dc_interlocking_generate_quotas(self, team_id, payload):
        res = self.service.post(f"{DC_INTERLOCKING_GENERATE_QUOTAS}"
                                f"?teamId={team_id}",
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=DC_INTERLOCKING_GENERATE_QUOTAS)
        return res

    @allure.step
    def get_dc_interlocking_statistics(self, team_id, job_id):
        res = self.service.get(f"{DC_INTERLOCKING_STATISTICS}"
                               f"?jobId={job_id}"
                               f"&teamId={team_id}",
                               cookies=self.cookies,
                               ep_name=DC_INTERLOCKING_STATISTICS)
        return res

    @allure.step
    def get_dc_interlocking_config_by_interlocking_id(self, interlocking_id, team_id):
        res = self.service.get(f"{DC_INTERLOCKING_CONFIG_BY_INTERLOCKING_ID}"
                               f"?teamId={team_id}"
                               f"&interlockingId={interlocking_id}",
                               cookies=self.cookies,
                               ep_name=DC_INTERLOCKING_CONFIG_BY_INTERLOCKING_ID)

        return res


class QualityFlowExternalApiProject(QualityFlowApi):
    def __init__(self, payload=None, env=None, api_key=None, session=None):
        custom_url = EXTERNAL_API_URL.format(pytest.env)
        super().__init__(custom_url=custom_url, payload=payload, env=env, api_key=api_key, session=session)

    @allure.step
    def post_create_project(self, team_id=None, payload=None, headers=None):
        res = self.service.post(f"{EXTERNAL_API_PROJECT_CREATE}"
                                f"?teamId={team_id}",
                                data=json.dumps(payload),
                                ep_name=PROJECT_CREATE,
                                headers=headers)
        return res

    @allure.step
    def post_upload_data_project(self, team_id=None, project_id=None, file_name=None, api_key=None):
        headers = {'Content-Type': 'text/csv',
                   "AUTHORIZATION": "Token token={token}".format(token=api_key)}

        with open(file_name) as file:
            data = file.read()
        res = self.service.post(f"{EXTERNAL_API_DATA_UPLOAD}"
                                f"?projectId={project_id}"
                                f"&teamId={team_id}"
                                f"&fileName={file_name}",
                                data=data.encode('utf-8'),
                                ep_name=EXTERNAL_API_DATA_UPLOAD,
                                headers=headers)
        return res

    @allure.step
    def post_download_data_project(self, team_id=None, project_id=None, payload=None, headers=None):
        res = self.service.post(f"{EXTERNAL_API_DATA_DOWNLOAD}"
                                f"?projectId={project_id}"
                                f"&teamId={team_id}",
                                data=json.dumps(payload),
                                ep_name=EXTERNAL_API_DATA_UPLOAD,
                                headers=headers)
        return res

    @allure.step
    def get_download_data_status_project(self, location=None, headers=None):
        res = self.service.get(f"/{location}",
                               headers=headers)

        return res

    @allure.step
    def get_content_downloadable_url_project(self, url=None):
        res = requests.get(f"{url}")

        return res

    def wait_until_download_ready(self, status, max_time=0, location=None, headers=None):
        wait = 2
        running_time = 0
        current_status = ""
        response = None
        while (current_status != status) and (running_time < max_time):
            res = self.get_download_data_status_project(location, headers)
            res.assert_response_status(202)
            current_status = res.json_response['status']
            running_time += wait
            time.sleep(wait)
            response = res.json_response

        return response.get('downloadableUrl')


class QualityFlowApiMetrics(QualityFlowApi):
    """
    https://api-kepler.integration.cf3.us/metrics/swagger-ui/index.html#/
    """

    def __init__(self, custom_url=None, payload=None, env=None, api_key=None, session=None):
        super().__init__(custom_url=custom_url, payload=payload, env=env, api_key=api_key, session=session)

    @allure.step
    def post_metrics_productivity_job_throughput(self, team_id, payload):
        res = self.service.post(f"{METRICS_PRODUCTIVITY_JOB_THROUGHPUT}"
                                f"?teamId={team_id}",
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=METRICS_PRODUCTIVITY_JOB_THROUGHPUT
                                )

        return res

    @allure.step
    def post_metrics_quality_project_quality(self, team_id, project_id):
        res = self.service.post(f"{METRICS_QUALITY_PROJECT_QUALITY}"
                                f"?teamId={team_id}"
                                f"&projectId={project_id}",
                                cookies=self.cookies,
                                ep_name=METRICS_QUALITY_PROJECT_QUALITY
                                )

        return res

    @allure.step
    def post_metrics_quality_leading_job_statistic(self, team_id, payload):
        res = self.service.post(f"{METRICS_QUALITY_LEADING_JOB_STATISTIC}"
                                f"?teamId={team_id}",
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=METRICS_QUALITY_LEADING_JOB_STATISTIC
                                )

        return res

    @allure.step
    def post_metrics_contributor_qachecker_performance(self, team_id, payload):
        res = self.service.post(f"{METRICS_CONTRIBUTOR_QACHECKER_PERFORMANCE}"
                                f"?teamId={team_id}",
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=METRICS_CONTRIBUTOR_QACHECKER_PERFORMANCE
                                )

        return res

    @allure.step
    def post_metrics_contributor_performance(self, team_id, payload):
        res = self.service.post(f"{METRICS_CONTRIBUTOR_PERFORMANCE}"
                                f"?teamId={team_id}",
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=METRICS_CONTRIBUTOR_PERFORMANCE
                                )

        return res

    @allure.step
    def post_metrics_project_job_statistic_progress(self, team_id, project_id, payload):
        res = self.service.post(f"{METRICS_PROJECT_JOB_STATISTIC_PROGRESS}"
                                f"?teamId={team_id}"
                                f"&projectId={project_id}",
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=METRICS_PROJECT_JOB_STATISTIC_PROGRESS
                                )

        return res

    @allure.step
    def post_metrics_project_job_statistic_breakdown_word_error_rate(self, team_id, payload):
        res = self.service.post(f"{METRICS_PROJECT_JOB_STATISTIC_BREAKDOWN_WORD_ERROR_RATE}"
                                f"?teamId={team_id}",
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=METRICS_PROJECT_JOB_STATISTIC_BREAKDOWN_WORD_ERROR_RATE
                                )

        return res

    @allure.step
    def post_metrics_project_job_statistic_breakdown_word_detail(self, team_id, payload):
        res = self.service.post(f"{METRICS_PROJECT_JOB_STATISTIC_BREAKDOWN_WORD_DETAIL}"
                                f"?teamId={team_id}",
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=METRICS_PROJECT_JOB_STATISTIC_BREAKDOWN_WORD_DETAIL
                                )

        return res

    @allure.step
    def post_metrics_project_job_statistic_breakdown_tag_summary(self, team_id, payload):
        res = self.service.post(f"{METRICS_PROJECT_JOB_STATISTIC_BREAKDOWN_TAG_SUMMARY}"
                                f"?teamId={team_id}",
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=METRICS_PROJECT_JOB_STATISTIC_BREAKDOWN_TAG_SUMMARY
                                )

        return res

    @allure.step
    def post_metrics_project_job_statistic_breakdown_tag_error_rate(self, team_id, payload):
        res = self.service.post(f"{METRICS_PROJECT_JOB_STATISTIC_BREAKDOWN_TAG_ERROR_RATE}"
                                f"?teamId={team_id}",
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=METRICS_PROJECT_JOB_STATISTIC_BREAKDOWN_TAG_ERROR_RATE
                                )

        return res

    @allure.step
    def post_metrics_project_job_statistic_breakdown_tag_detail(self, team_id, payload):
        res = self.service.post(f"{METRICS_PROJECT_JOB_STATISTIC_BREAKDOWN_TAG_DETAIL}"
                                f"?teamId={team_id}",
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=METRICS_PROJECT_JOB_STATISTIC_BREAKDOWN_TAG_DETAIL
                                )

        return res

    @allure.step
    def post_metrics_project_job_statistic_breakdown_label_error_rate(self, team_id, payload):
        res = self.service.post(f"{METRICS_PROJECT_JOB_STATISTIC_BREAKDOWN_LABEL_ERROR_RATE}"
                                f"?teamId={team_id}",
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=METRICS_PROJECT_JOB_STATISTIC_BREAKDOWN_LABEL_ERROR_RATE
                                )

        return res

    @allure.step
    def post_metrics_project_job_statistic_breakdown_label_detail(self, team_id, payload):
        res = self.service.post(f"{METRICS_PROJECT_JOB_STATISTIC_BREAKDOWN_LABEL_DETAIL}"
                                f"?teamId={team_id}",
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=METRICS_PROJECT_JOB_STATISTIC_BREAKDOWN_LABEL_DETAIL
                                )

        return res

    @allure.step
    def get_metrics_project_feedback_statistics(self, team_id, project_id):
        res = self.service.get(f"{METRICS_PROJECT_FEEDBACK_STATISTICS}"
                               f"?teamId={team_id}"
                               f"&projectId={project_id}",
                               cookies=self.cookies,
                               ep_name=METRICS_PROJECT_FEEDBACK_STATISTICS
                               )

        return res

    @allure.step
    def get_metrics_project_feedback_columns(self, team_id, project_id):
        res = self.service.get(f"{METRICS_PROJECT_FEEDBACK_COLUMNS}"
                               f"?teamId={team_id}"
                               f"&projectId={project_id}",
                               cookies=self.cookies,
                               ep_name=METRICS_PROJECT_FEEDBACK_COLUMNS
                               )

        return res

    @allure.step
    def post_metrics_project_feedback_list(self, team_id, project_id, payload):
        res = self.service.post(f"{METRICS_PROJECT_FEEDBACK_LIST}"
                                f"?teamId={team_id}"
                                f"&projectId={project_id}",
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=METRICS_PROJECT_FEEDBACK_LIST
                                )

        return res

    @allure.step
    def post_metrics_project_job_statistic_review_breakdown_word_error_rate(self, team_id, payload):
        res = self.service.post(f"{METRICS_PROJECT_JOB_STATISTIC_REVIEW_BREAKDOWN_WORD_ERROR_RATE}"
                                f"?teamId={team_id}",
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=METRICS_PROJECT_JOB_STATISTIC_REVIEW_BREAKDOWN_WORD_ERROR_RATE
                                )

        return res

    @allure.step
    def post_metrics_project_job_statistic_review_breakdown_word_detail(self, team_id, payload):
        res = self.service.post(f"{METRICS_PROJECT_JOB_STATISTIC_REVIEW_BREAKDOWN_WORD_DETAIL}"
                                f"?teamId={team_id}",
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=METRICS_PROJECT_JOB_STATISTIC_REVIEW_BREAKDOWN_WORD_DETAIL
                                )

        return res

    @allure.step
    def post_metrics_quality_review_job_statistic(self, team_id, payload):
        res = self.service.post(f"{METRICS_QUALITY_REVIEW_JOB_STATISTIC}"
                                f"?teamId={team_id}",
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=METRICS_QUALITY_REVIEW_JOB_STATISTIC
                                )

        return res

    @allure.step
    def post_metrics_project_job_statistic_review_breakdown_tag_summary(self, team_id, payload):
        res = self.service.post(f"{METRICS_PROJECT_JOB_STATISTIC_REVIEW_BREAKDOWN_TAG_SUMMARY}"
                                f"?teamId={team_id}",
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=METRICS_PROJECT_JOB_STATISTIC_REVIEW_BREAKDOWN_TAG_SUMMARY
                                )

        return res

    @allure.step
    def post_metrics_project_job_statistic_review_breakdown_tag_error_rate(self, team_id, payload):
        res = self.service.post(f"{METRICS_PROJECT_JOB_STATISTIC_REVIEW_BREAKDOWN_TAG_ERROR_RATE}"
                                f"?teamId={team_id}",
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=METRICS_PROJECT_JOB_STATISTIC_REVIEW_BREAKDOWN_TAG_ERROR_RATE
                                )

        return res

    @allure.step
    def post_metrics_project_job_statistic_review_breakdown_tag_detail(self, team_id, payload):
        res = self.service.post(f"{METRICS_PROJECT_JOB_STATISTIC_REVIEW_BREAKDOWN_TAG_DETAIL}"
                                f"?teamId={team_id}",
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=METRICS_PROJECT_JOB_STATISTIC_REVIEW_BREAKDOWN_TAG_DETAIL
                                )

        return res

    @allure.step
    def post_metrics_project_job_statistic_review_breakdown_label_error_rate(self, team_id, payload):
        res = self.service.post(f"{METRICS_PROJECT_JOB_STATISTIC_REVIEW_BREAKDOWN_LABEL_ERROR_RATE}"
                                f"?teamId={team_id}",
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=METRICS_PROJECT_JOB_STATISTIC_REVIEW_BREAKDOWN_LABEL_ERROR_RATE
                                )

        return res

    @allure.step
    def post_metrics_project_job_statistic_review_breakdown_label_detail(self, team_id, payload):
        res = self.service.post(f"{METRICS_PROJECT_JOB_STATISTIC_REVIEW_BREAKDOWN_LABEL_DETAIL}"
                                f"?teamId={team_id}",
                                data=json.dumps(payload),
                                cookies=self.cookies,
                                ep_name=METRICS_PROJECT_JOB_STATISTIC_REVIEW_BREAKDOWN_LABEL_DETAIL
                                )

        return res


class QualityFlowApiDistribution(QualityFlowApi):
    """
        https://api-kepler.integration.cf3.us/dist/swagger-ui/index.html#/
    """

    def __init__(self, custom_url=None, payload=None, env=None, api_key=None, session=None):
        super().__init__(custom_url=custom_url, payload=payload, env=env, api_key=api_key, session=session)

    @allure.step
    def get_distribution_fetch(self, params):
        original_url, self.service.base_url = self.service.base_url, self.kepler_internal_api_gateway_url
        ep_param = f"{DISTRIBUTION_FETCH}?jobId={params['jobId']}&workerId={params['workerId']}"
        if params.get('pageNum'):
            ep_param += f"&pageNum={params.get('pageNum')}"
        res = self.service.get(ep_param,
                               cookies=self.cookies,
                               ep_name=DISTRIBUTION_FETCH)
        self.service.base_url = original_url
        return res

    @allure.step
    def post_distribution_commit(self, payload):
        original_url, self.service.base_url = self.service.base_url, self.kepler_internal_api_gateway_url
        headers = {"Content-Type": 'application/json', "Accept": 'application/json'}
        res = self.service.post(DISTRIBUTION_COMMIT,
                                data=json.dumps(payload),
                                headers=headers,
                                cookies=self.cookies,
                                ep_name=DISTRIBUTION_COMMIT)
        self.service.base_url = original_url
        return res

    @allure.step
    def post_distribution_review(self, payload):
        original_url, self.service.base_url = self.service.base_url, self.kepler_internal_api_gateway_url
        headers = {"Content-Type": 'application/json', "Accept": 'application/json'}
        res = self.service.post(DISTRIBUTION_REVIEW,
                                data=json.dumps(payload),
                                headers=headers,
                                cookies=self.cookies,
                                ep_name=DISTRIBUTION_REVIEW)
        self.service.base_url = original_url
        return res

    @allure.step
    def post_distribution_save_commit_group(self, payload):
        original_url, self.service.base_url = self.service.base_url, self.kepler_internal_api_gateway_url
        headers = {"Content-Type": 'application/json', "Accept": 'application/json'}
        res = self.service.post(DISTRIBUTION_SAVE_COMMIT_GROUP,
                                data=json.dumps(payload),
                                headers=headers,
                                cookies=self.cookies,
                                ep_name=DISTRIBUTION_SAVE_COMMIT_GROUP)
        self.service.base_url = original_url
        return res

    @allure.step
    def post_distribution_save_review_group(self, payload):
        original_url, self.service.base_url = self.service.base_url, self.kepler_internal_api_gateway_url
        headers = {"Content-Type": 'application/json', "Accept": 'application/json'}
        res = self.service.post(DISTRIBUTION_SAVE_REVIEW_GROUP,
                                data=json.dumps(payload),
                                headers=headers,
                                cookies=self.cookies,
                                ep_name=DISTRIBUTION_SAVE_REVIEW_GROUP)
        self.service.base_url = original_url
        return res

    @allure.step
    def post_distribution_commit_group(self, payload):
        original_url, self.service.base_url = self.service.base_url, self.kepler_internal_api_gateway_url
        headers = {"Content-Type": 'application/json', "Accept": 'application/json'}
        res = self.service.post(DISTRIBUTION_COMMIT_GROUP,
                                data=json.dumps(payload),
                                headers=headers,
                                cookies=self.cookies,
                                ep_name=DISTRIBUTION_COMMIT_GROUP)
        self.service.base_url = original_url
        return res

    @allure.step
    def post_distribution_review_group(self, payload):
        original_url, self.service.base_url = self.service.base_url, self.kepler_internal_api_gateway_url
        headers = {"Content-Type": 'application/json', "Accept": 'application/json'}
        res = self.service.post(DISTRIBUTION_REVIEW_GROUP,
                                data=json.dumps(payload),
                                headers=headers,
                                cookies=self.cookies,
                                ep_name=DISTRIBUTION_REVIEW_GROUP)
        self.service.base_url = original_url
        return res
