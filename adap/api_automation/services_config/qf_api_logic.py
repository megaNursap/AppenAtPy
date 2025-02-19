"""
Quality flow API service for Perf calling, etc.
"""
import datetime
import json
import time
import allure
import pytest
import random
import gevent
import os
import logging
import pandas as pd

logging.getLogger('faker').setLevel(logging.ERROR)
from faker import Faker
from adap.perf_platform.utils.logging import get_logger
from adap.perf_platform.utils import error_handler as eh
from requests.sessions import HTTPAdapter
from adap.api_automation.services_config.endpoints.quality_flow_endpoints import *
from adap.api_automation.services_config.quality_flow import QualityFlowApi, QualityFlowApiProject, \
    QualityFlowApiContributor, QualityFlowApiWork, QualityFlowApiDistribution, QualityFlowApiMetrics
from adap.api_automation.utils.data_util import get_data_file, get_user_api_key, get_user_team_id, get_user_email, \
    get_user_password, get_user
from adap.e2e_automation.services_config.job_api_support import generate_job_link
from adap.settings import Config

LOGGER_PERF = os.environ.get("LOGGER_PERF")
if LOGGER_PERF == "True":
    log = get_logger(__name__)
else:
    log = logging.getLogger(__name__)
    logging.basicConfig(level=logging.DEBUG)
faker = Faker()
_today = datetime.datetime.now().strftime("%Y_%m_%d")


class EnvType:
    DEVSPACE = 'DEVSPACE'
    DEV = 'dev'
    SANDBOX = 'sandbox'
    INTEGRATION = 'integration'
    PRODUCTION = 'production'


class TestType:
    API = "API"
    UI = "UI"
    PERF = "PERF"


class JobType:
    JUDGMENT_OVERWRITE = "JUDGMENT_OVERWRITE"
    RESOLUTION = "RESOLUTION"
    WORK = "WORK"
    QA = "QA"


class QaOpType:
    QA_MODIFIABLE = "Allow the QA contributor to modify the original contributor's judgments"
    QA_REJECTED_TO_REWORK = "Do not allow QA Contributor to modify judgments and " \
                            "Automatically send rejected units back to the original contributor to be redone"
    QA_REJECTED_NO_OP = "Do not allow QA Contributor to modify judgments and " \
                        "Do not automatically send rejected units back to be redone"


class QaReviewResult:
    ACCEPTED = "ACCEPTED"  # Equal to ACCEPTED without judgment changed
    MODIFIED = "MODIFIED"  # Equal to ACCEPTED with judgment changed
    REJECTED = "REJECTED"


class CommitPayloadType:
    SPLIT = "SPLIT"
    AGG = "AGG"
    RANDOMIZED = "RANDOMIZED"


class InvoiceStatisticsType:
    UNIT_COUNT = "UNIT_COUNT"
    DURATION = "DURATION"


class UnitGroupOption:
    RETAIN = "RETAIN"
    IGNORE = "IGNORE"


class ReviewReasonOption:
    SINGLE = "SINGLE"
    MULTIPLE = "MULTIPLE"


class DataType:
    Textarea = 'Textarea'
    AudioTX = 'Audio_Transcription'


def generate_csv(num_rows=1000, segmentation=False, num_group=1000, header_size=3, save_path=None, batch_no="x"):
    """
    num_rows: number of csv rows except for csv header
    segmentation: special csv header '_Unit_Group' for segmented scenario of Quality Flow
    num_group: number of unit group
    header_size: number of headers except for '_Unit_Group', max header size supported by Quality Flow is 1000
                 minimum header size is 3, for Audio TX
    """
    seg = num_rows // num_group

    if segmentation:
        column_list = ['_Unit_Group', 'audio_name', 'audio_annotation', 'audio_url']
        sample_value_list = [
            None, f'audio_file_bn_{batch_no}_segroup_no_%s_seg_%s',
            'https://appen-pe-chn.s3.ap-southeast-1.amazonaws.com/kepler/Audio%2BTools__USA_USA_001_unit.json',
            'https://yaoxu.s3-us-west-2.amazonaws.com/Audio+Tools/F1068M1068_USA_USA_001.wav'
        ]
        header_size += 1
    else:
        column_list = ['audio_name', 'audio_annotation', 'audio_url']
        sample_value_list = [
            f'audio_file_bn{batch_no}_no_%s',
            'https://appen-pe-chn.s3.ap-southeast-1.amazonaws.com/kepler/Audio%2BTools__USA_USA_001_unit.json',
            'https://yaoxu.s3-us-west-2.amazonaws.com/Audio+Tools/F1068M1068_USA_USA_001.wav'
        ]

    original_size = len(column_list)
    if header_size > original_size:
        for i in range(header_size - original_size):
            column_list.append(f'Extend_Col{i + 1}')

    csv_content = ",".join(column_list)
    for i in range(num_rows):
        row_value = sample_value_list.copy()
        if segmentation:
            row_value[0] = str(i // seg + 1)
            row_value[1] = row_value[1] % (i // seg + 1, i % seg + 1)
        else:
            row_value[0] = row_value[0] % (i + 1)
        for j in range(header_size - original_size):
            row_value.append(f'Extend_Col{i + 1}_{faker.pystr()}')
        csv_content += '\n' + ", ".join(row_value)

    if save_path is not None:
        with open(save_path, 'w') as f:
            f.write(csv_content)
    else:
        return csv_content


class QualityFlowApiSingletonManager(QualityFlowApiProject,
                                     QualityFlowApiContributor,
                                     QualityFlowApiWork,
                                     QualityFlowApiDistribution,
                                     QualityFlowApiMetrics):
    env = None
    qf = None
    cookies = None
    _sid = None
    team_id = None

    def __init__(self, *args, **kwargs):
        super(QualityFlowApiSingletonManager, self).__init__(*args, **kwargs)

    @staticmethod
    def get_singleton_instance():
        env = QualityFlowApiSingletonManager.env

        if QualityFlowApiSingletonManager.qf is None:
            QualityFlowApiSingletonManager.qf = QualityFlowApiSingletonManager(env=env, session=True)

        return QualityFlowApiSingletonManager.qf

    @staticmethod
    def set_env(env, team_id):
        QualityFlowApiSingletonManager.env = env
        QualityFlowApiSingletonManager.team_id = team_id

    @staticmethod
    def set_perf():
        qf = QualityFlowApiSingletonManager.qf
        qf.service.request.mount("http://", HTTPAdapter(pool_connections=1, pool_maxsize=10000, max_retries=0))
        qf.service.request.mount("https://", HTTPAdapter(pool_connections=1, pool_maxsize=10000, max_retries=0))

    @staticmethod
    def logic_qf_login(username, password):
        qf = QualityFlowApiSingletonManager.qf

        QualityFlowApiSingletonManager.cookies = qf.get_valid_sid(username, password)

    @staticmethod
    def logic_set_cookies(cookies):
        QualityFlowApiSingletonManager.cookies = cookies
        QualityFlowApiSingletonManager.qf.set_cookies(cookies)

    @staticmethod
    def logic_create_qf_project(name, desc, unit_seg_type="UNIT_ONLY"):
        qf = QualityFlowApiSingletonManager.qf
        team_id = QualityFlowApiSingletonManager.team_id

        payload = {
            "name": name,
            "description": desc,
            # "unitSegmentType": unit_seg_type
        }

        res = qf.post_create_project(team_id=team_id, payload=payload)
        assert res.json_response['code'] == 200
        response = res.json_response

        return response.get("data")

    @staticmethod
    def get_payload_batch_number(round_id):
        payload = {
            "startRow": 0,
            "endRow": 999,
            "filterModel": {
                "sourceFileBatchNumber": {
                    "filter": round_id,
                    "filterTo": None,
                    "filterType": "number",
                    "type": "equals"
                }
            },
            "sortModel": [],
            "queryString": ""
        }
        return payload

    @staticmethod
    def logic_fetch_project_units_by_job_id(project_id, job_id, worker_id, job_status, round_id):
        qf = QualityFlowApiSingletonManager.qf
        team_id = QualityFlowApiSingletonManager.team_id
        payload = QualityFlowApiSingletonManager.get_payload_batch_number(round_id)
        payload['filterModel'].update({
            "jobId": {
                "filter": job_id,
                "filterType": "text",
                "type": "equals"
            },
            "history.workerId": {
                "filter": worker_id,
                "filterType": "text",
                "type": "equals"
            },
            "jobStatus": {
                "values": job_status,
                "filterType": "set"
            }
        })

        res = qf.post_units(project_id, team_id, payload)
        # log.info(res.text)
        assert res.json_response["code"] == 200
        return res.json_response["data"]

    @staticmethod
    def logic_pm_upload_units(project_id, env, round_id, csv_file=None, gcc=None):
        qf = QualityFlowApiSingletonManager.qf
        team_id = QualityFlowApiSingletonManager.team_id
        log.info(f'Upload coroutine {round_id} Start: project_id - {project_id}, env - {env}')

        if gcc is None:
            if csv_file is None:
                # None means default setting automatically
                audio_csv_file = get_data_file('/audio_tx_sample_unit_1000.csv', env)
            else:
                audio_csv_file = get_data_file(f'/{csv_file}', env)
            unit_number = len(pd.read_csv(audio_csv_file))
            with open(audio_csv_file, 'r', encoding='utf-8-sig') as f:
                csv_data = f.read()
        else:
            csv_data = generate_csv(num_rows=gcc.get('num_rows'), segmentation=gcc.get('segmentation'),
                                    num_group=gcc.get('num_group'), header_size=gcc.get('header_size'),
                                    save_path=gcc.get('save_path'), batch_no=str(round_id))
            unit_number = gcc.get('num_rows')
            audio_csv_file = f"auto_gen_csv_file_unit_num_{unit_number}.csv"

        log.info(f"unit_number - {unit_number}, audio_csv_file - {audio_csv_file}")
        res = qf.get_file_upload_url(project_id, team_id, audio_csv_file)
        # log.info(f"Response - {res.text}")
        S3_url = res.json_response["data"]["presignedUrl"]
        id = res.json_response["data"]["id"]
        # log.info(f"S3_url - {S3_url}")
        base_url_bak, qf.service.base_url = qf.service.base_url, ''
        headers = {
            "accept": "*/*",
            "content-type": "text/csv"
        }
        qf.service.put(S3_url, headers=headers, data=csv_data.encode('utf-8'))
        qf.service.base_url = base_url_bak
        # This interval seems a must, or else, the following '/project/files' will always get 'UPLOADING' status
        time.sleep(5)
        res = qf.post_notify_file(team_id, publish="true", payload={
            "id": id,
            "projectId": project_id,
            "result": "success",
            "version": 0
        }, ignore_warning="false")
        if res.json_response['code'] == 3007:
            res = qf.post_notify_file(team_id, publish="true", payload={
                "id": id,
                "message": "",
                "projectId": project_id,
                "result": "success",
                "statusCode": "200",
                "version": 0
            }, ignore_warning="true")

        res = qf.get_list_of_files_for_project(project_id, team_id, page_num=0, page_size=1)
        count = 0
        while count < 60 and res.json_response["data"]["content"][0]["status"] != "PUBLISHED":
            time.sleep(5)
            res = qf.get_list_of_files_for_project(project_id, team_id, page_num=0, page_size=1)
            count += 1
        assert res.json_response["data"]["content"][0]["status"] == "PUBLISHED"
        # res = qf.get_list_of_downloaded_files(project_id, team_id, data_type="DATA_SET")
        # assert res.json_response["message"] == "success"
        payload = QualityFlowApiSingletonManager.get_payload_batch_number(round_id)
        res = qf.post_units(project_id, team_id, payload)
        count = 0
        while count < 60 and res.json_response["data"]["totalElements"] != unit_number:
            time.sleep(5)
            res = qf.post_units(project_id, team_id, payload)
            count += 1
        assert res.json_response["data"]["totalElements"] == unit_number
        for unit in res.json_response["data"]["units"]:
            assert unit["jobStatus"][0]["value"] == "NEW"
        log.info(f'Upload coroutine {round_id} End')
        # number = random.randint(0, 100)
        # log.info(f'Waiting {number} second')
        # gevent.sleep(number)
        return unit_number

    @staticmethod
    def pm_multi_upload(project_id, env):
        qf = QualityFlowApiSingletonManager.qf
        team_id = QualityFlowApiSingletonManager.team_id
        coroutines = [gevent.spawn(QualityFlowApiSingletonManager.logic_pm_upload_units, project_id, env, i + 1) for i
                      in range(100)]
        gevent.joinall(coroutines)
        res = qf.get_project_data_summary(project_id, team_id)
        assert res.json_response["data"]["totalUnits"] == 100000
        assert res.json_response["data"]["newUnits"] == 100000
        log.info(f'Upload successfully')

    @staticmethod
    def logic_pm_send_units_to_job(project_id, job_id, round_id, job_name=None, unit_num_check=False, unit_number=None,
                                   filter_model=False):
        qf = QualityFlowApiSingletonManager.qf
        team_id = QualityFlowApiSingletonManager.team_id
        payload = QualityFlowApiSingletonManager.get_payload_batch_number(round_id)
        if not filter_model:
            res = qf.post_units(project_id, team_id, payload)
            count = 0
            while count < 30 and len(res.json_response["data"]["units"]) != unit_number:
                time.sleep(2)
                res = qf.post_units(project_id, team_id, payload)
                count += 1
            assert res.json_response["data"]["totalElements"] == unit_number
            assert len(res.json_response["data"]["units"]) == unit_number
            units_1000 = [res.json_response['data']['units'][i]['unitId'][0]['value'] for i in range(unit_number)]

            res = qf.post_send_to_job(job_id, team_id, payload={
                "projectId": project_id,
                "unitIds": units_1000,
                "percentage": 100
            })
            assert res.json_response['code'] == 200
        else:
            res = qf.post_send_to_job(job_id, team_id, payload={
                "projectId": project_id,
                "filterModel": {
                    "jobStatus": {
                        "values": ["NEW"],
                        "filterType": "set"
                    },
                    "sourceFileBatchNumber": {
                        "type": "equals",
                        "filter": round_id,
                        "filterTo": None,
                        "filterType": "number"
                    }
                },
                "percentage": 100
            })
        assert res.json_response['code'] == 200
        assert res.json_response['message'] == 'success'
        assert res.json_response['data']['total'] == unit_number
        assert res.json_response['data']['error'] is False
        if unit_num_check:
            payload['filterModel'].update({
                "jobId": {
                    "filter": job_id,
                    "filterType": "text",
                    "type": "equals"
                }
            })
            res = qf.post_units(project_id, team_id, payload)
            count = 0
            while count < 30 and len(res.json_response["data"]["units"]) != unit_number:
                time.sleep(2)
                res = qf.post_units(project_id, team_id, payload)
                count += 1
            assert res.json_response["data"]["totalElements"] == unit_number
            assert len(res.json_response["data"]["units"]) == unit_number
            for i in range(unit_number):
                assert res.json_response['data']['units'][i]['jobStatus'][0]['value'] == 'ASSIGNED'
                assert job_id in res.json_response['data']['units'][i]['jobAlias'][0]['link']
                if job_name is not None:
                    assert res.json_response['data']['units'][i]['jobTitle'][0]['value'] == job_name
                assert res.json_response['data']['units'][i]['jobId'][0]['value'] == job_id
        time.sleep(60)

    @staticmethod
    def logic_pm_send_all_new_units_to_job(project_id, job_id):
        qf = QualityFlowApiSingletonManager.qf
        team_id = QualityFlowApiSingletonManager.team_id
        res = qf.post_send_to_job(job_id, team_id, payload={
            "projectId": project_id,
            "filterModel": {
                "jobStatus": {
                    "values": ["NEW"],
                    "filterType": "set"
                }
            },
            "queryString": "",
            "percentage": 100
        })
        assert res.json_response['code'] == 200
        assert res.json_response['message'] == 'success'
        unit_number = res.json_response['data']['total']
        time.sleep(unit_number * 0.06)

    @staticmethod
    # +------------------------------Logic of Curated Crowd------------------------------------------
    def logic_curated_crowd_criteria_search_by_project_id(project_id, setting_id,
                                                          default_page_size=10000, default_page_num=1):
        qf = QualityFlowApiSingletonManager.qf
        team_id = QualityFlowApiSingletonManager.team_id

        payload = {
            "pageSize": default_page_size,
            "pageNum": default_page_num,
            "projectId": project_id,
            "filterModel": {},
            "query": "",
            "settingId": setting_id
        }
        res = qf.post_contributor_crowd_criteria_search(team_id, payload)
        if res.json_response.get("code") is None:
            log.info(f"ERR: {res.json_response}")
        assert res.json_response["code"] == 200
        return res.json_response["data"]

    @staticmethod
    def logic_curated_crowd_assign_contributor_to_job(project_id, contributor_list, job_id):
        qf = QualityFlowApiSingletonManager.qf
        team_id = QualityFlowApiSingletonManager.team_id

        payload = {
            "projectId": project_id,
            "jobId": job_id,
            "contributorIds": contributor_list
        }
        res = qf.post_contributor_crowd_assign_job(team_id, payload)
        log.info(res.json_response)
        assert res.json_response["code"] == 200
        return res.json_response["data"]

    @staticmethod
    def logic_curated_crowd_test_create_contributor(project_id, number):
        qf = QualityFlowApiSingletonManager.qf

        res = qf.post_contributor_test_create_contributor(project_id, number, qf.team_id)
        assert res.json_response["code"] == 200
        return res.json_response["data"]

    # +------------------------------Logic of Distribution--------------------------------------------------------------
    @staticmethod
    def logic_distribution_polling_fetch(job_id, worker_id, max_polling_times=50, interval=0.1, max_duration=10,
                                         fetch_page_num=None):
        qf = QualityFlowApiSingletonManager.qf
        count = 0
        errmsg = None
        remainingWorkCount = None
        start_time = time.time()
        # segment_fetched_list = []
        fetched_flag = False
        while count < max_polling_times:
            data = qf.logic_distribution_fetch_and_submit(job_id, worker_id, just_fetch_flag=True,
                                                          fetch_page_num=fetch_page_num)
            if data is not None and data['distributions'] is not None:
                # for distribution in data['distributions']:
                #     for segment in distribution['segments']:
                # segment_fetched_list.append({
                #     "segmentGroupId": segment["segmentGroupId"],
                #     "segmentSequence": segment["segmentSequence"]
                # })
                remainingWorkCount = data['remainingWorkCount']
                fetched_flag = True
                break
            elif data is not None and data['remainingWorkCount'] == 0:
                errmsg = 'remainingWorkCount=0'
                remainingWorkCount = 0
                log.info(errmsg)
                break
            elif data is not None and data['distributions'] is None and data['remainingWorkCount'] != 0:
                remainingWorkCount = data['remainingWorkCount']
                errmsg = f"'distributions=None&remainingWorkCount={remainingWorkCount}"
                log.info(errmsg)
                break
            else:
                time.sleep(interval)
                count += 1

            real_duration = time.time() - start_time
            if real_duration > max_duration:
                log.info(f'{real_duration}s ({count + 1}) Duration exceeds the maximum polling time. Then exit.')
                break

        end_time = time.time()
        cost = float('%0.3f' % (end_time - start_time))
        data_dist = data['distributions'] if fetched_flag else None
        log.info('Fetching tasks costs %f Seconds (%s rounds)' % (cost, count + 1))

        return {
            "time": cost,
            "dataDist": data_dist,
            "remainingWorkCount": remainingWorkCount,
            "errmsg": errmsg,
            "pageNum": data.get('pageNum'),
            "pageSize": data.get('pageSize'),
            "totalPages": data.get('totalPages')
        }

    @staticmethod
    def logic_distribution_commit(worker_id, dist, auto_judgment=True, auto_judgment_source_col_name=None,
                                  judgment_keys=["sample_text_area"], judgment={}, audio_tx_judgment={},
                                  commit_payload_type=CommitPayloadType.AGG, commit_type="COMMIT",
                                  abandon_percentage=0, data_type=DataType.Textarea):
        qf = QualityFlowApiSingletonManager.qf
        segment_counter = 0
        abandon_flag = False
        for i in range(len(dist)):
            fm_dist = {
                "id": dist[i]["id"],
                "workerId": dist[i]["workerId"],
                "segments": []
            }
            if len(dist[i]['segments']) > 1:
                log.info("Labeling work task page shouldn't contain more than 1 distribution segment per distribution!")
                return None
            for j in range(len(dist[i]['segments'])):
                if auto_judgment:
                    judgment = {}
                    for k in judgment_keys:
                        if data_type == DataType.Textarea:
                            judgment[k] = "J"
                        elif data_type == DataType.AudioTX:
                            judgment[k] = audio_tx_judgment[list(audio_tx_judgment.keys())[random.randint(0, 2)]]["WORK"]
                fm_segment = {
                    "id": dist[i]['segments'][j]["id"],
                    "workerId": dist[i]['segments'][j]["workerId"],
                    "judgment": judgment
                }
                if random.randint(0, 99) < abandon_percentage:
                    fm_segment['reviewResult'] = "ABANDONED"
                    fm_segment['judgment'] = None
                    abandon_flag = True
                fm_dist["segments"].append(fm_segment)
                segment_counter += 1
            dist[i] = fm_dist

        if commit_payload_type == CommitPayloadType.AGG \
                or commit_payload_type == CommitPayloadType.RANDOMIZED and random.randint(0, 1) == 1:
            dist_agg_dict = {}
            for item in dist:
                if item['id'] in dist_agg_dict:
                    dist_agg_dict[item['id']]['segments'].extend(item['segments'])
                else:
                    dist_agg_dict[item['id']] = item
            dist = []
            for k, v in dist_agg_dict.items():
                dist.append(v)

        if commit_type == "COMMIT" or abandon_flag:
            res = qf.post_distribution_commit(dist)
        elif commit_type == "SAVE_GROUP" and not abandon_flag:
            res = qf.post_distribution_save_group(dist)
        elif commit_type == "COMMIT_GROUP" or (commit_type == "SAVE_GROUP" and abandon_flag):
            res = qf.post_distribution_commit_group(dist)
        else:
            raise ValueError(f"commit_type:{commit_type} is not supported!")
        log.info(f'Worker {worker_id} worked {segment_counter} segments.')
        assert res.json_response.get("code") is not None, f"HTTPCODE:{res.status_code}, BODY:{res.json_response}"
        assert res.json_response.get(
            "code") == 200, f"{res.status_code}: Worker_id: {worker_id}, Distribution Commit http code isn't 200, code[{res.json_response.get('code')}], msg[{res.json_response.get('message')}]"

        return res.json_response['data']

    @staticmethod
    def logic_distribution_review(worker_id, dist, review_result_list=[QaReviewResult.ACCEPTED],
                                  judgment_keys=["sample_text_area"], audio_tx_judgment={}, job_type=JobType.QA,
                                  review_type="REVIEW", abandon_percentage=0, data_type=DataType.Textarea,
                                  feedback_result_list=[QaReviewResult.ACCEPTED]):
        qf = QualityFlowApiSingletonManager.qf
        segment_counter = 0
        N = len(review_result_list)
        abandon_flag = False
        for i in range(len(dist)):
            fm_dist = {
                "id": dist[i]["id"],
                "workerId": dist[i]["workerId"],
                "segments": []
            }
            # for j in range(len(dist[i]['segments'])):
            fm_segment = {
                "id": dist[i]['segments'][-1]["id"],
                "workerId": dist[i]['segments'][-1]["workerId"],
                "judgment": {}
            }
            segment_counter += 1
            review_result = review_result_list[random.randint(0, len(review_result_list) - 1)]
            feedback_result = feedback_result_list[random.randint(0, len(feedback_result_list) - 1)]
            if job_type == JobType.WORK:
                fm_segment['reviewResult'] = feedback_result
                fm_segment['reviewComment'] = f"WORK {feedback_result}"
            if job_type == JobType.QA and review_result == QaReviewResult.MODIFIED:
                for k in judgment_keys:
                    if data_type == DataType.Textarea:
                        fm_segment['judgment'][k] = f'{fm_segment["judgment"][k]} - mod by QA {fm_segment["workerId"]}'
                    elif data_type == DataType.AudioTX:
                        fm_segment['judgment'][k] = audio_tx_judgment[list(audio_tx_judgment.keys())[random.randint(0, 2)]]["QA"]
                fm_segment['reviewResult'] = QaReviewResult.ACCEPTED
                fm_segment['reviewComment'] = f"{job_type} {QaReviewResult.MODIFIED}"
                if random.randint(0, 99) < abandon_percentage:
                    fm_segment['reviewResult'] = "ABANDONED"
                    fm_segment['judgment'] = None
                    abandon_flag = True
            fm_segment['reviewResult'] = review_result
            fm_segment['reviewComment'] = f"{job_type} {review_result}"
            fm_dist["segments"].append(fm_segment)
            dist[i] = fm_dist

        if review_type == "REVIEW" or abandon_flag:
            res = qf.post_distribution_review(dist)
        elif review_type == "SAVE_GROUP" and not abandon_flag:
            res = qf.post_distribution_save_group(dist)
        elif review_type == "REVIEW_GROUP" or (review_type == "SAVE_GROUP" and abandon_flag):
            res = qf.post_distribution_review_group(dist)
        else:
            raise ValueError(f"review_type:{review_type} is not supported!")
        log.info(f'QA {worker_id} reviewed {segment_counter} segments.')
        assert res.json_response.get("code") is not None, f"HTTPCODE:{res.status_code}, BODY:{res.json_response}"
        assert res.json_response[
                   "code"] == 200, f"{res.status_code}: Worker_id: {worker_id}, Distribution Review http code isn't 200, code[{res.json_response.get('code')}], msg[{res.json_response.get('message')}]"
        return res.json_response['data']

    @staticmethod
    def logic_distribution_fetch_and_submit(job_id, worker_id, working_seconds_per_task_page=1, job_type=JobType.WORK,
                                            qa_job_op=QaOpType.QA_MODIFIABLE, just_fetch_flag=False, retrieve_data={},
                                            review_result_list=[QaReviewResult.ACCEPTED],
                                            feedback_result_list=[QaReviewResult.ACCEPTED],
                                            auto_judgment=True, auto_judgment_source_col_name=None,
                                            judgment_keys=["sample_text_area"], judgment={"sample_text_area": "J"},
                                            audio_tx_judgment={}, fetch_page_num=None,
                                            commit_payload_type=CommitPayloadType.AGG,
                                            abandon_percentage=0, data_type=DataType.Textarea):
        """
        Submit including commit and review
        """
        qf = QualityFlowApiSingletonManager.qf
        params = {
            "jobId": job_id,
            "workerId": worker_id
        }
        if fetch_page_num is not None:
            params["pageNum"] = fetch_page_num
        res = qf.get_distribution_fetch(params)
        assert res.json_response.get("code") is not None, f"HTTPCODE:{res.status_code}, BODY:{res.json_response}"
        assert res.json_response.get(
            "code") == 200, f"{res.status_code}: Worker_id: {worker_id}, Distribution Fetch http code isn't 200, code[{res.json_response.get('code')}], msg[{res.json_response.get('message')}]"
        if just_fetch_flag:
            return res.json_response.get("data")
        res_dict = json.loads(res.text)
        dist = res_dict['data']['distributions']
        current_fetched_page_num = res_dict['data'].get('pageNum')
        current_fetched_page_size = res_dict['data'].get('pageSize')
        current_fetched_total_pages = res_dict['data'].get('totalPages')
        LEN_OF_DIST = 0 if dist is None else len(dist)
        segment_counter = 0
        review_flag = False
        N = len(review_result_list)
        NF = len(feedback_result_list)
        abandon_flag = False
        for i in range(LEN_OF_DIST):
            fm_dist = {
                "id": dist[i]["id"],
                "workerId": dist[i]["workerId"],
                "segments": []
            }

            # for j in range(len(dist[i]['segments'])):
            if len(dist[i]['segments']):
                fm_segment = {
                    "id": dist[i]['segments'][-1]["id"],
                    "workerId": dist[i]['segments'][-1]["workerId"],
                    "judgment": {}
                }
            else:
                log.info(f"Something wrong: distribution.segment list is empty!")
                continue

            segment_counter += 1
            review_result = review_result_list[random.randint(0, len(review_result_list)-1)]  # review_result_list[(segment_counter - 1) % N]  # ACCEPTED/REJECTED, MODIFIED
            feedback_result = feedback_result_list[random.randint(0, len(feedback_result_list)-1)]  # feedback_result_list[(segment_counter - 1) % NF]  # ACCEPTED/REJECTED

            if job_type == JobType.WORK and len(dist[i]['segments']) == 1:
                if auto_judgment:
                    for k in judgment_keys:
                        if data_type == DataType.Textarea:
                            fm_segment['judgment'][k] = "J"
                        elif data_type == DataType.AudioTX:
                            fm_segment['judgment'][k] = audio_tx_judgment[list(audio_tx_judgment.keys())[random.randint(0, 2)]]["WORK"]
                else:
                    fm_segment['judgment'] = judgment
                # fm_dist["segments"].append(fm_segment)
                if random.randint(0, 99) < abandon_percentage:
                    fm_segment['reviewResult'] = "ABANDONED"
                    fm_segment['judgment'] = None
                    abandon_flag = True
            elif job_type == JobType.WORK and len(dist[i]['segments']) > 1:
                # feedback review by worker
                review_flag = True
                fm_segment['reviewResult'] = feedback_result
                fm_segment['reviewComment'] = f"WORK {feedback_result}"
                if qa_job_op == QaOpType.QA_MODIFIABLE:
                    # worker's, QA's, worker's feedback review distributions
                    pass
                elif qa_job_op == QaOpType.QA_REJECTED_TO_REWORK or qa_job_op == QaOpType.QA_REJECTED_NO_OP:
                    # QA's, worker's feedback review distributions
                    pass
            elif job_type == JobType.QA:
                review_flag = True
                if review_result == QaReviewResult.MODIFIED:
                    # fm_segment['judgment']["Judgment QA Modified"] = True
                    for k in judgment_keys:
                        if data_type == DataType.Textarea:
                            fm_segment['judgment'][
                                k] = f'{dist[i]["segments"][-1].get("judgment").get(k)} - mod by QA {fm_segment["workerId"]}'
                        elif data_type == DataType.AudioTX:
                            judgment_key = [j for j in audio_tx_judgment.keys() if j in str(dist[i]["segments"][-1].get("judgment").get(k))]
                            fm_segment['judgment'][k] = audio_tx_judgment[judgment_key[0]]["QA"]
                    fm_segment['reviewResult'] = QaReviewResult.ACCEPTED
                    fm_segment['reviewComment'] = f"QA {QaReviewResult.MODIFIED}"
                else:
                    fm_segment['reviewResult'] = review_result
                    fm_segment['reviewComment'] = f"QA {review_result}"
                if random.randint(0, 99) < abandon_percentage:
                    fm_segment['reviewResult'] = "ABANDONED"
                    fm_segment['judgment'] = None
                    abandon_flag = True

            fm_dist["segments"].append(fm_segment)
            if retrieve_data.get('segment_fetch_sequence_list') is not None:
                retrieve_data.get('segment_fetch_sequence_list').append({
                    "segmentGroupId": dist[i]['segments'][-1]["segmentGroupId"],
                    "segmentSequence": dist[i]['segments'][-1]["segmentSequence"]
                })
            dist[i] = fm_dist

        time.sleep(working_seconds_per_task_page)  # working seconds per task page

        if LEN_OF_DIST and (commit_payload_type == CommitPayloadType.AGG
                            or commit_payload_type == CommitPayloadType.RANDOMIZED and random.randint(0, 1) == 1):
            dist_agg_dict = {}
            for item in dist:
                if item['id'] in dist_agg_dict:
                    dist_agg_dict[item['id']]['segments'].extend(item['segments'])
                else:
                    dist_agg_dict[item['id']] = item
            dist = []
            for k, v in dist_agg_dict.items():
                dist.append(v)

        fetch_info = {
            "fetch_page_num": current_fetched_page_num,
            "fetch_total_pages": current_fetched_total_pages,
            "fetch_page_size": current_fetched_page_size,
            "fetch_dist_num": LEN_OF_DIST,
            "abandon_flag": abandon_flag
        }
        if LEN_OF_DIST:
            if review_flag:
                if fetch_page_num is not None:
                    if current_fetched_page_num == current_fetched_total_pages or abandon_flag:
                        res = qf.post_distribution_review_group(dist)
                    else:
                        res = qf.post_distribution_save_review_group(dist)
                else:
                    res = qf.post_distribution_review(dist)
            else:
                if fetch_page_num is not None:
                    if current_fetched_page_num == current_fetched_total_pages or abandon_flag:
                        res = qf.post_distribution_commit_group(dist)
                    else:
                        res = qf.post_distribution_save_commit_group(dist)
                else:
                    res = qf.post_distribution_commit(dist)
            log.info(f'{job_type} {worker_id} submitted {segment_counter} segments.')
            assert res.json_response.get("code") is not None, f"HTTPCODE:{res.status_code}, BODY:{res.json_response}"
            assert res.json_response.get(
                "code") == 200, f"{res.status_code}: Worker_id: {worker_id}, Distribution Submit http code isn't 200, code[{res.json_response.get('code')}], msg[{res.json_response.get('message')}]"

            return res.json_response.get("data"), fetch_info
        else:
            log.info(f'Nothing is fetched and needed to submit.')
            return None, fetch_info

    # +------------------------------Logic of main process--------------------------------------------------------------
    @staticmethod
    def logic_create_quality_flow(project_name=None, project_desc=None, project_id=None, unit_seg_type="UNIT_ONLY",
                                  serial_label="A", start_from_scratch=True, flow_define=None,
                                  job_launch_flag=True, create_standard_data=False, cml_setting=None,
                                  job_name_prefix="", sample_define=None, env=EnvType.INTEGRATION,
                                  csv_upload=None, csv_upload_batch_no=1, ontology_setting=None):
        """Create a project, quality flow, data and launch it"""
        qf = QualityFlowApiSingletonManager.qf

        if project_name is None:
            project_name = 'PJ%s' % time.strftime('%Y%m%d%H%M%S', time.localtime())
        if project_desc is None:
            project_desc = 'api_auto_project'

        # Step 1. Create a Project
        if project_id is None:
            data = qf.logic_create_qf_project(project_name, project_desc, unit_seg_type)
            project_id = data['id']
        # project_display_id = data['displayId']
        # Step 2. Import csv to a Project (unit/segment)
        if csv_upload is not None:
            # Not None means needing uploading unit csv
            qf.logic_pm_upload_units(project_id, env, csv_upload_batch_no, csv_file=csv_upload)
        # Step 3. Create a Quality Flow (Job_1, Job_2)
        # SBO = ['SEND_BACK_TO_SAME_CONTRIBUTOR', 'SEND_BACK_TO_POOL', 'NO_OP']
        # --changeable for need--
        if flow_define is None:
            # None means default setting automatically
            flow_define = [
                ["WORK", {"judgments_per_row": '1', "rows_per_page": 5, "assignment_lease_expiry": 60,
                          "invoiceStatisticsType": InvoiceStatisticsType.UNIT_COUNT, "payRateType": "Work",
                          "maxJudgmentPerContributorEnabled": "false", "maxJudgmentPerContributor": 0,
                          "allowAbandonUnits": "true", "unitGroupOption": UnitGroupOption.IGNORE}],
                ["QA", {"judgments_per_row": '1', "rows_per_page": 5, "assignment_lease_expiry": 60,
                        "invoiceStatisticsType": InvoiceStatisticsType.UNIT_COUNT, "payRateType": "QA",
                        "maxJudgmentPerContributorEnabled": "false", "maxJudgmentPerContributor": 0,
                        "allowSelfQa": "false",
                        "allowAbandonUnits": "true",
                        "judgment_modifiable": 'true', "send_back_op": 'NO_OP', "feedback": "ENABLED",
                        "reviewReasonOption": ReviewReasonOption.SINGLE, "reviewReasons": "TER\\nWER\\nLER\\nTSER"}],
                # ["QA", {"judgments_per_row": '1', "rows_per_page": 5, "assignment_lease_expiry": 120,
                #         "judgment_modifiable": 'true', "send_back_op": SBO[1]}],
                # ["QA", {"judgments_per_row": '1', "rows_per_page": 5, "assignment_lease_expiry": 120,
                #         "judgment_modifiable": 'true', "send_back_op": SBO[2]}],
                # ["QA", {"judgments_per_row": '1', "rows_per_page": 2, "assignment_lease_expiry": 120, "judgment_modifiable": 'true', "send_back_op": SBO[0]}]
            ]
        if sample_define is None:
            # None means default setting automatically
            sample_define = [
                {},
                {"sampleRate": 100, "segmental": False, "segmentSampleRate": 100},
                # {"sampleRate": 100, "filterCriteria": "{}", "filterNum": 0, "frequencyPeriod": 2, "frequencyUnit": "HOURS"},
            ]
        unit_size = 10
        segment_per_unit = 1
        # --changeable for need--
        job_id_list = []
        flow_id = None  # "c8d7e2fe-69de-4113-a621-a53d3291f16a"  # Flow A series
        leading_job_type = flow_define[0][0]
        job_number = len(flow_define)

        if not start_from_scratch:
            template_title = "Audio Transcription"  # "Product Categorization"
            res = qf.get_job_templates()
            for temp in res.json_response:
                if temp['title'] == template_title:
                    template_id = temp['job_id']
            res = qf.get_template_job(template_id)
            template_cml = {
                "instructions": res.json_response["instructions"],
                "cml": res.json_response["cml"],
                "js": res.json_response["js"],
                "css": res.json_response["css"]
            }
        else:
            template_title = "No use template"
            template_cml = {
                "instructions": '',
                "cml": cml_setting if cml_setting is not None else '',
                "js": '',
                "css": ''
            }
        cml_QA = {
            "instructions": '',
            "cml": '',
            "js": '',
            "css": ''
        }
        for i in range(job_number):
            job_type = leading_job_type if i == 0 else "QA"
            template_display_name = template_title  # if i == 0 else "No use template"
            cml = template_cml if i == 0 else cml_QA
            job_title = "%s%s_JOB_%s%s" % (job_name_prefix, job_type, serial_label, i + 1)
            create_job_params = {
                "teamId": qf.team_id,
                "projectId": project_id,
                "flowId": flow_id,
                "type": job_type,
                "title": job_title,
                "templateType": {
                    "index": 1
                },
                "templateDisplayNm": template_display_name,
                "cml": cml
            }
            if i == 0:
                res1 = qf.post_create_job_v2(qf.team_id, create_job_params)
                assert res1.json_response["code"] == 200
                assert res1.json_response["data"]["cycleNumber"] == i
                flow_id = res1.json_response["data"]["flowId"]
                job_id_list.append({
                    "id": res1.json_response["data"]["id"],
                    "version": res1.json_response["data"]["version"]
                })
                res2 = qf.get_job_with_cml(qf.team_id, res1.json_response["data"]["id"])
                rsp2 = res2.json_response
                data = rsp2['data']
                cml_QA['instructions'] = data['instructions']
                if leading_job_type == "WORK":
                    cml_QA['cml'] = data['cml'] + cml_QA['cml']
                else:
                    cml_QA['cml'] = data['cml']
                cml_QA['js'] = data['js']
                cml_QA['css'] = data['css']
                # CML configure
                res3 = qf.get_job_with_cml(qf.team_id, job_id_list[-1].get("id"))
                rsp3 = res3.json_response
                job_with_cml = rsp3['data']
                payload = {
                    "id": job_with_cml["cmlId"],
                    "version": job_with_cml["cmlVersion"],
                    "teamId": qf.team_id,
                    "jobId": job_with_cml["id"],
                    "flowId": job_with_cml["flowId"],
                    "instructions": job_with_cml["instructions"],
                    "cml": cml_setting,
                    "js": job_with_cml["js"],
                    "css": job_with_cml["css"],
                    "tags": job_with_cml["tags"],
                    "validators": job_with_cml["validators"],
                    "isValid": job_with_cml["isValid"]
                }
                res = qf.put_cml(qf.team_id, payload)
                assert res.json_response['code'] == 200
                # Ontology configure
                if ontology_setting is not None:
                    payload = {
                        "resource_team_id": qf.team_id,
                        "resource_type": "ontology",
                        "resource_contents": ontology_setting
                    }
                    res = qf.post_resource(team_id=qf.team_id, job_id=job_id_list[-1].get("id"),
                                           resource_type='ontology', payload=payload)
                    assert res.status_code == 204, 'Ontology setting failed.'
            else:
                clone_job_payload = {
                    "copiedFrom": job_id_list[i - 1]["id"],
                    "appendTo": job_id_list[i - 1]["id"],
                    "teamId": qf.team_id,
                    "projectId": project_id,
                    "title": "%s%s_JOB_%s%s" % (job_name_prefix, job_type, serial_label, i + 1),
                    # "includeLaunchConfig": False
                    "types": ["DESIGN"]
                }
                res1 = qf.post_clone_job_v2(qf.team_id, clone_job_payload)
                assert res1.json_response["code"] == 200
                # assert res1.json_response["data"]["cycleNumber"] == i
                # flow_id = res1.json_response["data"]["flowId"]
                job_id_list.append({
                    "id": res1.json_response["data"]["id"],
                    "version": None
                })
                # CML copy
                # qf.post_cml_clone(qf.team_id, job_id_list[i]["id"], job_id_list[i-1]["id"])
        # Step 4. Sample/Send units to a Quality Flow
        last_node = "project_data_source"
        for i in range(len(job_id_list)):
            job_id = job_id_list[i]["id"]
            if i >= len(sample_define) or not sample_define[i] or sample_define[i] == {}:
                last_node = job_id
                continue
            body_data_tpl = {
                "projectId": project_id,
                "teamId": qf.team_id,
                "origin": last_node,
                "appliedJobId": job_id,
                "sampleRate": sample_define[i]["sampleRate"],
                # "fixedUnitNum": 1
            }
            body_data = body_data_tpl.copy()
            if i == 0:
                body_data["recursive"] = 'true'
                body_data["schedulerDelay"] = sample_define[i]["frequencyPeriod"]
                body_data["schedulerUnit"] = sample_define[i]["frequencyUnit"]
                body_data["filterCriteria"] = sample_define[i]["filterCriteria"]
                body_data["filterNum"] = sample_define[i]["filterNum"]
            else:
                body_data["schedulerDelay"] = 0
                body_data["schedulerUnit"] = "HOURS"
                body_data["segmental"] = sample_define[i]["segmental"]
                body_data["segmentSampleRate"] = sample_define[i]["segmentSampleRate"]
            # res = qf.post_job_filter(qf.team_id, body_data)
            payload = {
                "id": job_id,
                "jobFilter": body_data
            }
            res = qf.put_update_job_v2(qf.team_id, payload)
            assert res.json_response["code"] == 200
            last_node = job_id
        # Step 5. Launch Job_1 and Job_2
        if job_launch_flag:
            for i in range(len(job_id_list)):
                job_info = job_id_list[i]
                res3 = qf.get_job_with_cml(qf.team_id, job_info['id'])
                rsp3 = res3.json_response
                job_with_cml = rsp3['data']
                # Job QUALITY page setting
                if job_with_cml['type'] == 'QA':
                    # job_with_cml['judgmentModifiable'] = flow_define[i][1]['judgment_modifiable']
                    # job_with_cml['sendBackOp'] = flow_define[i][1]['send_back_op']
                    put_job_payload = {
                        "id": job_with_cml['id'],
                        "teamId": qf.team_id,
                        "templateType": job_with_cml['templateType'],
                        "title": job_with_cml['title'],
                        "version": job_with_cml['version'],
                        "judgmentModifiable": flow_define[i][1]['judgment_modifiable'],
                        "sendBackOp": flow_define[i][1]['send_back_op'],
                        "feedback": flow_define[i][1]['feedback'],
                        "reviewReasonOption": flow_define[i][1]['reviewReasonOption'],
                        "reviewReasons": flow_define[i][1]['reviewReasons']
                    }
                    res = qf.put_update_job_v2(qf.team_id, put_job_payload)
                    # job_info['version'] = res.json_response['data']['version']
                # Job LAUNCH Crowd Settings
                put_job_payload = {
                    "id": job_with_cml['id'],
                    "jobCrowd": {"crowdType": ["INTERNAL", "EXTERNAL"], "crowdSubType": "APPEN_CONNECT"}
                }
                res = qf.put_update_job_v2(qf.team_id, put_job_payload)
                # job_info['version'] = res.json_response['data']['version']
                # Job LAUNCH Prices & Row Settings
                job_launch_config_payload = {
                    "id": job_info['id'],
                    # "teamId": qf.team_id,
                    # "version": job_info['version'],
                    "judgmentsPerRow": flow_define[i][1]['judgments_per_row'],
                    "rowsPerPage": flow_define[i][1]['rows_per_page'],
                    "assignmentLeaseExpiry": flow_define[i][1]['assignment_lease_expiry'],
                    # "displayContributorName": False,
                    # "strictTiming": False,
                    "invoiceStatisticsType": flow_define[i][1]['invoiceStatisticsType'],
                    "payRateType": flow_define[i][1]['payRateType'],
                    "maxJudgmentPerContributorEnabled": flow_define[i][1]['maxJudgmentPerContributorEnabled'],
                    "maxJudgmentPerContributor": flow_define[i][1]['maxJudgmentPerContributor'],
                    "allowAbandonUnits": flow_define[i][1]['allowAbandonUnits']
                }
                # Specific setting for leading job
                if i == 0:
                    job_launch_config_payload["unitGroupOption"] = flow_define[i][1]['unitGroupOption']
                if flow_define[i][0] == JobType.QA:
                    job_launch_config_payload["allowSelfQa"] = flow_define[i][1]['allowSelfQa']
                res4 = qf.put_update_job_v2(qf.team_id, job_launch_config_payload)
                # Launch Job
                # res5 = qf.post_launch_job_v2(qf.team_id, job_info['id'])

        if create_standard_data:
            pass
        # time.sleep(5)  # need this or BE gives "Current job can't be the state" 400 error: javax.persistence.OptimisticLockException: Row was updated or deleted by another transaction (or unsaved-value mapping was incorrect)
        # Step 6. Preview Job
        for job_id in job_id_list:
            qf.post_job_preview_v2(qf.team_id, job_id["id"])

        # Step 7. Resume Job
        for job_id in job_id_list:
            qf.post_job_resume_v2(qf.team_id, job_id["id"])

        for job_id in job_id_list:
            log.debug(f'job_id: {job_id.get("id")}')

        return project_id, job_id_list

    @staticmethod
    def logic_curated_crowd_ac_setting_and_syncing(project_id, ac_id, sync_type):
        qf = QualityFlowApiSingletonManager.qf

        # step 1. Create AC syncing setting
        payload = {
            "projectId": project_id,
            "externalName": "APPEN_CONNECT",
            "externalProjectId": ac_id,
            "syncType": sync_type
        }
        res = qf.post_contributor_sync_setting_create(qf.team_id, payload)
        rsp = res.json_response

        assert rsp.get('code') == 200
        data = rsp.get('data')

        # step 4. Select 'Target all Appen Connect contributors' and Save
        payload_update_effect = data
        payload_update_effect['syncType'] = sync_type
        res = qf.put_contributor_sync_setting_update_effect(qf.team_id, payload_update_effect)
        rsp = res.json_response

        assert rsp.get('code') == 200
        setting_id = rsp.get('data').get('settingId')

        # step 5. Polling until setting saved and ac users synced
        MAX_LOOP = 30
        count = 0
        while True:
            count += 1
            res = qf.get_contributor_sync_setting_detail(qf.team_id, setting_id=setting_id)
            rsp = res.json_response

            last_synced = rsp.get('data').get('lastSynced')
            if count > MAX_LOOP or last_synced is not None:
                break
            else:
                time.sleep(3)

        assert last_synced is not None

        return {
            "setting_id": setting_id
        }

    @staticmethod
    def logic_assign_contributor_to_job(project_id, contributor_ids, job_id):
        qf = QualityFlowApiSingletonManager.qf

        payload = {
            "projectId": project_id,
            "contributorIds": contributor_ids,
            "jobId": job_id
        }
        res = qf.post_contributor_crowd_assign_job(qf.team_id, payload)
        rsp = res.json_response
        assert rsp['code'] == 200

    @staticmethod
    def logic_curated_crowd_link_ac_sync_setting_to_job(project_id, job_id, setting_id):
        qf = QualityFlowApiSingletonManager.qf

        payload = {
            "projectId": project_id,
            "jobId": job_id,
            "settingId": setting_id
        }
        res = qf.post_contributor_sync_setting_job_link(qf.team_id, payload)
        rsp = res.json_response
        assert rsp['code'] == 200

    @staticmethod
    def logic_create_and_launch_leading_job(project_id, job_type, job_title, target_job_status="RUNNING", cml="",
                                            instructions="",
                                            job_crowd={"crowdType": ["INTERNAL"]}, judgments_per_row=1, rows_per_page=5,
                                            assignment_lease_expiry=1800, allow_abandon_units=False,
                                            invoice_statistics_type=InvoiceStatisticsType.UNIT_COUNT, pay_rate_type="",
                                            max_judgment_per_contributor_enabled=False, max_judgment_per_contributor=0,
                                            unit_group_option=UnitGroupOption.RETAIN):
        qf = QualityFlowApiSingletonManager.qf

        # Step 1. Create a new job
        res = qf.post_create_job_v2(team_id=qf.team_id, payload={
            "title": job_title,
            "teamId": qf.team_id,
            "projectId": project_id,
            "type": job_type})
        assert res.json_response["code"] == 200
        job_id = res.json_response['data']['id']

        # Step 2. Configure cml
        res = qf.get_job_with_cml(qf.team_id, job_id)
        rsp = res.json_response
        assert rsp['code'] == 200

        job_with_cml = rsp['data']
        payload = {
            "id": job_with_cml["cmlId"],
            "version": job_with_cml["cmlVersion"],
            "teamId": qf.team_id,
            "jobId": job_with_cml["id"],
            "flowId": job_with_cml["flowId"],
            "instructions": instructions,
            "cml": cml,
            "js": job_with_cml["js"],
            "css": job_with_cml["css"],
            "tags": job_with_cml["tags"],
            "validators": job_with_cml["validators"],
            "isValid": job_with_cml["isValid"]
        }
        res = qf.put_cml(qf.team_id, payload)
        assert res.json_response["code"] == 200

        # Step 3. Job launch setting
        # Job Crowd Settings
        put_job_payload = {
            "id": job_id,
            "jobCrowd": job_crowd
        }
        res = qf.put_update_job_v2(qf.team_id, put_job_payload)
        assert res.json_response["code"] == 200
        # Job LAUNCH Prices & Row Settings
        job_launch_config_payload = {
            "id": job_id,
            "judgmentsPerRow": judgments_per_row,
            "rowsPerPage": rows_per_page,
            "assignmentLeaseExpiry": assignment_lease_expiry,
            "invoiceStatisticsType": invoice_statistics_type,
            "payRateType": pay_rate_type,
            "maxJudgmentPerContributorEnabled": max_judgment_per_contributor_enabled,
            "maxJudgmentPerContributor": max_judgment_per_contributor,
            "allowAbandonUnits": allow_abandon_units,
            "unitGroupOption": unit_group_option
        }
        res = qf.put_update_job_v2(qf.team_id, job_launch_config_payload)
        assert res.json_response["code"] == 200

        # Step 4. Preview Job
        if target_job_status in ["RUNNING", "PAUSED"]:
            res = qf.post_job_preview_v2(qf.team_id, job_id)
            assert res.json_response["code"] == 200

        # Step 5. Resume Job
        if target_job_status == "RUNNING":
            res = qf.post_job_resume_v2(qf.team_id, job_id)
            assert res.json_response["code"] == 200

        return job_id

    @staticmethod
    def logic_create_and_launch_following_job(project_id, preceding_job_id, job_title, target_job_status="RUNNING",
                                              judgment_modifiable=True, feedback="ENABLED", send_back_op='NO_OP',
                                              review_reason_option=ReviewReasonOption.SINGLE, review_reasons="",
                                              job_crowd={"crowdType": ["INTERNAL"]}, judgments_per_row=1,
                                              rows_per_page=5,
                                              assignment_lease_expiry=1800, allow_abandon_units=False,
                                              invoice_statistics_type=InvoiceStatisticsType.UNIT_COUNT,
                                              pay_rate_type="",
                                              max_judgment_per_contributor_enabled=False,
                                              max_judgment_per_contributor=0,
                                              allow_self_qa=False
                                              ):
        qf = QualityFlowApiSingletonManager.qf

        # Step 1. Create a new following job
        clone_job_payload = {
            "copiedFrom": preceding_job_id,
            "appendTo": preceding_job_id,
            "teamId": qf.team_id,
            "projectId": project_id,
            "title": job_title,
            "types": ["DESIGN"]
        }
        res = qf.post_clone_job_v2(qf.team_id, clone_job_payload)
        assert res.json_response["code"] == 200
        job_id = res.json_response["data"]["id"]

        # Step 2. Job launch setting
        # Job Crowd Settings
        put_job_payload = {
            "id": job_id,
            "jobCrowd": job_crowd
        }
        res = qf.put_update_job_v2(qf.team_id, put_job_payload)
        assert res.json_response["code"] == 200
        # Job LAUNCH Prices & Row Settings
        job_launch_config_payload = {
            "id": job_id,
            "judgmentsPerRow": judgments_per_row,
            "rowsPerPage": rows_per_page,
            "assignmentLeaseExpiry": assignment_lease_expiry,
            "invoiceStatisticsType": invoice_statistics_type,
            "payRateType": pay_rate_type,
            "maxJudgmentPerContributorEnabled": max_judgment_per_contributor_enabled,
            "maxJudgmentPerContributor": max_judgment_per_contributor,
            "allowAbandonUnits": allow_abandon_units,
            "allowSelfQa": allow_self_qa
        }
        res = qf.put_update_job_v2(qf.team_id, job_launch_config_payload)
        assert res.json_response["code"] == 200

        # Step 3. Preview job and Quality setting
        if target_job_status in ["RUNNING", "PAUSED"]:
            put_job_payload = {
                "id": job_id,
                "judgmentModifiable": judgment_modifiable,
                "sendBackOp": send_back_op,
                "feedback": feedback,
                "reviewReasonOption": review_reason_option,
                "reviewReasons": review_reasons
            }
            res = qf.put_update_job_v2(qf.team_id, put_job_payload)
            assert res.json_response["code"] == 200
            res = qf.post_job_preview_v2(qf.team_id, job_id)
            assert res.json_response["code"] == 200

        # Step 4. Resume Job
        if target_job_status == "RUNNING":
            res = qf.post_job_resume_v2(qf.team_id, job_id)
            assert res.json_response["code"] == 200

        return job_id
