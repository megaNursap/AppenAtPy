"""
### clone job feature major tests

# clone API
# https://api-kepler.integration.cf3.us/work/v2/job/clone
1. clone job leading WORK -> leading WORK
2. clone job leading QA -> leading QA
3. clone job leading WORK -> following QA
4. clone job leading QA -> following QA
5. clone job following QA -> leading QA
6. clone job following QA -> following QA

# appendable-as-collection API
# https://api-kepler.integration.cf3.us/work/job/appendable-as-collection
1. clonable job list should contains the active leading WORK/following QA jobs which don't have following job
   clonable job list should not contains the job which have following job
   clonable job list should not contains the 3rd job
2. clonable job list should not contains the DC WORK/QA jobs
3. clonable job list should not contains the deleted jobs


"""
import time

import pytest
from faker import Faker
import datetime

from adap.api_automation.services_config.quality_flow import QualityFlowApiWork, QualityFlowApiProject
from adap.api_automation.utils.data_util import get_test_data, get_user_team_id
from adap.ui_automation.services_config.quality_flow.components import login_and_open_qf_page


mark_env = pytest.mark.skipif(not pytest.running_in_preprod_integration, reason="for Integration env")

pytestmark = [pytest.mark.qf_api,
              pytest.mark.regression_qf,
              mark_env]

faker = Faker()
_today = datetime.datetime.now().strftime("%Y_%m_%d")

@pytest.fixture(scope="module")
def new_project():
    """
    create a new UNIT_ONLY test project
    create a leading work job A1 in flow A
    create a following QA job A2 in flow A
    create a leading QA job B1 in flow B
    create a leading work job C1 in flow C
    """
    username = get_test_data('qf_user', 'email')
    password = get_test_data('qf_user', 'password')
    team_id = get_user_team_id('qf_user')

    api = QualityFlowApiProject()
    api.get_valid_sid(username, password)

    # create a new UNIT_ONLY test project
    project_name = f"automation project {_today} {faker.zipcode()}: job clone feature test"
    payload = {"name": project_name,
               "description": project_name,
               "unitSegmentType": "UNIT_ONLY"}
    res = api.post_create_project(team_id=team_id, payload=payload)
    assert res.status_code == 200
    data = res.json_response.get('data')
    assert data, "Project data has not been found"
    project_id = data['id']

    job_api = QualityFlowApiWork()
    job_api.get_valid_sid(username, password)
    job_payload = {"title": f"New QF job {_today} {faker.zipcode()}",
                   "teamId": team_id,
                   "projectId": project_id,
                   "type": "WORK",
                   "flowId": '',
                   "templateDisplayNm": "No use template",
                   "templateType": {"index": 1},
                   "cml": {"js": "",
                           "css": "",
                           "cml": "<cml:audio_annotation source-data='{{audio_url}}' name='Annotate the thing' validates='required' />",
                           "instructions": "Test CML API update"},
                   "jobFilter": {
                       "projectId": project_id,
                       "origin": "project_data_source",
                       "schedulerDelay": 24,
                       "schedulerUnit": "HOURS",
                       "sampleRate": 10,
                       "segmental": False,
                       "segmentSampleRate": 100,
                       "filterCriteria": "{}",
                       "filterNum": 0,
                       "minimumSampleUnit": 0
                   }
                   }

    # create a leading work job A1 in flow A
    job_payload1 = {**job_payload, "title": f"Leading work job A1 in flow A {_today} {faker.zipcode()}"}
    res1 = job_api.post_create_job_v2(team_id=team_id, payload=job_payload1)
    assert res.status_code == 200
    leading_work_job = res1.json_response['data']['id']

    # create a following QA job A2 in flow A
    copy_payload = {
        "copiedFrom": leading_work_job,
        "appendTo": leading_work_job,
        "teamId": team_id,
        "projectId": project_id,
        "title": f"Following QA job A2 was copied {_today} {faker.zipcode()}",
        "types": ["DESIGN", "CROWD_SETTINGS", "PRICE_AND_ROW"]
    }
    # clone job leading WORK -> following QA
    res2 = job_api.post_clone_job(team_id=team_id, payload=copy_payload)
    assert res2.status_code == 200

    # create a leading QA job B1 in flow B
    job_payload3 = {**job_payload, "title": f"Leading QA job B1 in flow B {_today} {faker.zipcode()}", "type": "QA"}
    res3 = job_api.post_create_job_v2(team_id=team_id, payload=job_payload3)
    assert res2.status_code == 200

    # create a leading work job C1 in flow C
    job_payload3 = {**job_payload, "title": f"Leading WORK job C1 in flow C {_today} {faker.zipcode()}"}
    res4 = job_api.post_create_job_v2(team_id=team_id, payload=job_payload3)
    assert res4.status_code == 200

    return {
        "id": project_id,
        "team_id": data['teamId'],
        "version": data['version'],
        "jobs": [res.json_response['data']['id']],
        "job_api": job_api,
        "leading_work_job": res1.json_response['data']['id'],
        "following_QA_job": res2.json_response['data']['id'],
        "leading_QA_job": res3.json_response['data']['id'],
        "leading_work_job_flow_C": res4.json_response['data']['id']
    }
    # return {'id': '3e7c3560-b595-478b-9ca9-38ed377d8501', 'team_id': 'f8fb3aaf-f3f1-437a-9bb8-170c136e9084', 'version': 0, 'jobs': ['fd79c89f-1305-48d5-a778-b1476b487510']}


def test_clone_leading_work_job_as_leading_work_job(new_project):
    '''
        1. clone job from leading WORK -> leading WORK
        2. verified only ["DESIGN", "CROWD_SETTINGS", "PRICE_AND_ROW"] will be copied
        3. DESIGN including Ontology
    '''
    api = new_project['job_api']
    team_id = new_project['team_id']
    project_id = new_project['id']
    leading_work_job = new_project['leading_work_job']

    # Get jobs for project and save the jobs number
    res = api.get_job_all(team_id=team_id, project_id=project_id)
    assert res.status_code == 200
    assert res.json_response['message'] == 'success'
    data = res.json_response.get('data')
    jobs = data['content']
    title = f"Leading work job was copied {_today} {faker.zipcode()}"
    copy_payload = {
        "copiedFrom": leading_work_job,
        "appendTo": "project_data_source",
        "teamId": team_id,
        "projectId": project_id,
        "title": title,
        "types": ["DESIGN", "CROWD_SETTINGS", "PRICE_AND_ROW"]
    }
    # clone job leading WORK -> leading WORK
    res = api.post_clone_job(team_id=team_id, payload=copy_payload)
    assert res.status_code == 200
    assert res.json_response['message'] == 'success'
    data = res.json_response['data']
    assert data['title'] == title
    assert data['cycleNumber'] == 0
    assert data['flowId'] is not None
    assert data['feedback'] == "DISABLED"
    assert data['type'] == "WORK"
    assert data['state'] == "DRAFT"
    assert data['activeStatus'] == "ACTIVE"
    assert data['copiedFrom'] == leading_work_job
    assert data['assignmentLeaseExpiry'] == 1800
    assert data['judgmentsPerRow'] == 1
    assert data['rowsPerPage'] == 5
    assert data['displayContributorName'] is None
    assert data['judgmentModifiable'] is False
    assert data['sendBackOp'] == "NO_OP"
    assert data['maxJudgmentPerContributorEnabled'] is False
    assert data['maxJudgmentPerContributor'] == 0
    assert data['unitSegmentType'] == "UNIT_ONLY"
    assert data['internalSecret'] is not None

    assert data['payRateType'] is not None
    assert data['invoiceStatisticsType'] == "UNIT_COUNT"
    assert data['allowSelfQa'] is False
    assert data['allowAbandonUnits'] is True

    assert data['unitGroupOption'] == "RETAIN"
    assert data['active'] is True
    assert data['running'] is False

    assert data['multipleJudgment'] is False
    assert data['segmented'] is False
    assert data['appenConnectCrowd'] is False
    assert data['draft'] is True

    time.sleep(5)
    # check jobs for project
    res = api.get_job_all(team_id=team_id, project_id=project_id)
    assert res.status_code == 200
    assert res.json_response['message'] == 'success'

    data = res.json_response.get('data')
    new_jobs = data['content']
    assert len(jobs) + 1 == len(new_jobs)


def test_clone_leading_QA_job_as_leading_QA_job(new_project):
    '''
        1. clone job leading QA -> leading QA
        2. verified only ["DESIGN", "CROWD_SETTINGS", "PRICE_AND_ROW", "QUALITY_SETTINGS"] will be copied
        3. DESIGN including Ontology
    '''
    api = new_project['job_api']
    team_id = new_project['team_id']
    project_id = new_project['id']
    leading_QA_job = new_project['leading_QA_job']

    # Get jobs for project and save the jobs number
    res = api.get_job_all(team_id=team_id, project_id=project_id)
    assert res.status_code == 200
    assert res.json_response['message'] == 'success'
    data = res.json_response.get('data')
    jobs = data['content']

    copy_payload = {
        "copiedFrom": leading_QA_job,
        "appendTo": "project_data_source",
        "teamId": team_id,
        "projectId": project_id,
        "title": "Leading QA job was copied",
        "types": ["DESIGN", "CROWD_SETTINGS", "PRICE_AND_ROW", "QUALITY_SETTINGS"]
    }
    # clone job leading WORK -> leading WORK
    res = api.post_clone_job(team_id=team_id, payload=copy_payload)
    assert res.status_code == 200
    assert res.json_response['message'] == 'success'
    data = res.json_response['data']
    assert data['title'] == "Leading QA job was copied"
    assert data['cycleNumber'] == 0
    assert data['flowId'] is not None
    assert data['feedback'] == "DISABLED"
    assert data['type'] == "QA"
    assert data['state'] == "DRAFT"
    assert data['activeStatus'] == "ACTIVE"
    assert data['copiedFrom'] == leading_QA_job
    assert data['assignmentLeaseExpiry'] == 1800
    assert data['judgmentsPerRow'] == 1
    assert data['rowsPerPage'] == 5
    assert data['displayContributorName'] is None
    assert data['judgmentModifiable'] is False
    assert data['sendBackOp'] == "NO_OP"
    assert data['maxJudgmentPerContributorEnabled'] is False
    assert data['maxJudgmentPerContributor'] == 0
    assert data['unitSegmentType'] == "UNIT_ONLY"
    assert data['internalSecret'] is not None
    # assert data['jobCml'] == "<cml:audio_annotation source-data='{{audio_url}}' name='Annotate the thing' validates='required' />"   # current API alway return null cml for job
    # assert data['jobFilter'] == {
    #     "projectId": data['id'],
    #     "origin": "project_data_source",
    #     "schedulerDelay": 24,
    #     "schedulerUnit": "HOURS",
    #     "sampleRate": 10,
    #     "segmental": False,
    #     "segmentSampleRate": 100,
    #     "filterCriteria": "{}",
    #     "filterNum": 0,
    #     "minimumSampleUnit": 0
    # }
    assert data['jobCrowd'] is None
    # assert data['instruction'] == "Test CML API update"
    assert data['parentJobId'] is None

    assert data['payRateType'] is not None
    assert data['invoiceStatisticsType'] == "UNIT_COUNT"
    assert data['allowSelfQa'] is False
    assert data['allowAbandonUnits'] is True

    assert data['unitGroupOption'] == "RETAIN"
    assert data['active'] is True
    assert data['running'] is False

    assert data['multipleJudgment'] is False
    assert data['segmented'] is False
    assert data['appenConnectCrowd'] is False
    assert data['draft'] is True

    time.sleep(5)
    # check jobs for project
    res = api.get_job_all(team_id=team_id, project_id=project_id)
    assert res.status_code == 200
    assert res.json_response['message'] == 'success'

    data = res.json_response.get('data')
    new_jobs = data['content']
    assert len(jobs) + 1 == len(new_jobs)


def test_clone_leading_work_job_as_third_following_QA_job(new_project, app):
    '''
        1. clone job leading WORK -> following QA
        2. verified only ["DESIGN", "CROWD_SETTINGS", "PRICE_AND_ROW"] will be copied
        3. DESIGN including Ontology
    '''
    api = new_project['job_api']
    team_id = new_project['team_id']
    project_id = new_project['id']
    leading_work_job = new_project['leading_work_job']
    following_QA_job = new_project['following_QA_job']
    # leading_QA_job = new_project['leading_QA_job']

    # Get jobs for project and save the jobs number
    res = api.get_job_all(team_id=team_id, project_id=project_id)
    assert res.status_code == 200
    assert res.json_response['message'] == 'success'
    data = res.json_response.get('data')
    jobs = data['content']
    title = f"Third following QA job was copied {faker.zipcode()}"
    copy_payload = {
        "copiedFrom": leading_work_job,
        "appendTo": following_QA_job,
        "teamId": team_id,
        "projectId": project_id,
        "title": title,
        "types": ["DESIGN", "CROWD_SETTINGS", "PRICE_AND_ROW"]
    }
    # clone job leading WORK -> following QA
    res = api.post_clone_job(team_id=team_id, payload=copy_payload)
    assert res.status_code == 200
    assert res.json_response['message'] == 'success'
    data = res.json_response['data']
    third_job_id = data['id']
    assert data['title'] == title
    assert third_job_id is not None
    assert data['cycleNumber'] == 2
    assert data['flowId'] == leading_work_job
    assert data['feedback'] == "DISABLED"
    assert data['type'] == "QA"
    assert data['state'] == "DRAFT"
    assert data['activeStatus'] == "ACTIVE"
    assert data['copiedFrom'] == leading_work_job
    assert data['assignmentLeaseExpiry'] == 1800
    assert data['judgmentsPerRow'] == 1
    assert data['rowsPerPage'] == 5
    assert data['judgmentModifiable'] is False
    assert data['sendBackOp'] == "NO_OP"
    assert data['maxJudgmentPerContributorEnabled'] is False
    assert data['maxJudgmentPerContributor'] == 0
    assert data['unitSegmentType'] == "UNIT_ONLY"
    assert data['jobCrowd'] is None
    assert data['instruction'] is not None
    assert data['payRateType'] is not None
    assert data['invoiceStatisticsType'] == "UNIT_COUNT"
    assert data['allowSelfQa'] is False
    assert data['allowAbandonUnits'] is True

    assert data['unitGroupOption'] == "RETAIN"
    assert data['active'] is True
    assert data['running'] is False

    assert data['multipleJudgment'] is False
    assert data['segmented'] is False
    assert data['appenConnectCrowd'] is False
    assert data['draft'] is True

    time.sleep(5)
    # check jobs for project
    res = api.get_job_all(team_id=team_id, project_id=project_id)
    assert res.status_code == 200
    assert res.json_response['message'] == 'success'

    data = res.json_response.get('data')
    new_jobs = data['content']
    assert len(jobs) + 1 == len(new_jobs)

    # verify can't create new following job from web page
    # Only do the limitation from Front End, backend still can create it and new job will following as 4th job on the job flow
    login_and_open_qf_page(app, 'qf_user')
    time.sleep(5)
    app.quality_flow.open_jobs_page_by_project_id(project_id)
    app.quality_flow.assert_job_flow_have_no_create_button_for_new_following_job(third_job_id)


def test_clone_leading_QA_job_as_following_QA_job(new_project):
    '''
        1. clone job leading QA -> following QA
        2. verified only ["DESIGN", "CROWD_SETTINGS", "PRICE_AND_ROW", "QUALITY_SETTINGS", "SAMPLING"] will be copied
        3. DESIGN including Ontology
    '''
    api = new_project['job_api']
    team_id = new_project['team_id']
    project_id = new_project['id']
    leading_QA_job = new_project['leading_QA_job']
    leading_work_job_flow_C = new_project['leading_work_job_flow_C']

    # Get jobs for project and save the jobs number
    res = api.get_job_all(team_id=team_id, project_id=project_id)
    assert res.status_code == 200
    assert res.json_response['message'] == 'success'
    data = res.json_response.get('data')
    jobs = data['content']

    title = f"Following QA job was copied {faker.zipcode()}"
    copy_payload = {
        "copiedFrom": leading_QA_job,
        "appendTo": leading_work_job_flow_C,
        "teamId": team_id,
        "projectId": project_id,
        "title": title,
        "types": ["DESIGN", "CROWD_SETTINGS", "PRICE_AND_ROW", "QUALITY_SETTINGS", "SAMPLING"]
    }
    # clone job leading WORK -> leading WORK
    res = api.post_clone_job(team_id=team_id, payload=copy_payload)
    assert res.status_code == 200
    assert res.json_response['message'] == 'success'
    data = res.json_response['data']

    assert data['title'] == title
    assert data['cycleNumber'] == 1
    assert data['flowId'] == leading_work_job_flow_C
    assert data['feedback'] == "DISABLED"
    assert data['type'] == "QA"
    assert data['state'] == "DRAFT"
    assert data['activeStatus'] == "ACTIVE"
    assert data['copiedFrom'] == leading_QA_job
    assert data['assignmentLeaseExpiry'] == 1800
    assert data['judgmentsPerRow'] == 1
    assert data['rowsPerPage'] == 5
    assert data['displayContributorName'] is None
    assert data['judgmentModifiable'] is False
    assert data['sendBackOp'] == "NO_OP"
    assert data['maxJudgmentPerContributorEnabled'] is False
    assert data['maxJudgmentPerContributor'] == 0
    assert data['unitSegmentType'] == "UNIT_ONLY"
    assert data['internalSecret'] is not None
    # assert data['jobCml'] == "<cml:audio_annotation source-data='{{audio_url}}' name='Annotate the thing' validates='required' />"
    # assert data['jobFilter'] == {
    #                    "projectId": data['id'],
    #                    "origin": "project_data_source",
    #                    "schedulerDelay": 24,
    #                    "schedulerUnit": "HOURS",
    #                    "sampleRate": 10,
    #                    "segmental": False,
    #                    "segmentSampleRate": 100,
    #                    "filterCriteria": "{}",
    #                    "filterNum": 0,
    #                    "minimumSampleUnit": 0
    #                }
    assert data['jobCrowd'] is None
    assert data['parentJobId'] is None

    assert data['payRateType'] is not None
    assert data['invoiceStatisticsType'] == "UNIT_COUNT"
    assert data['allowSelfQa'] is False
    assert data['allowAbandonUnits'] is True

    assert data['unitGroupOption'] == "RETAIN"
    assert data['active'] is True
    assert data['running'] is False

    assert data['multipleJudgment'] is False
    assert data['segmented'] is False
    assert data['appenConnectCrowd'] is False
    assert data['draft'] is True
    time.sleep(5)
    # check jobs for project
    res = api.get_job_all(team_id=team_id, project_id=project_id)
    assert res.status_code == 200
    assert res.json_response['message'] == 'success'

    data = res.json_response.get('data')
    new_jobs = data['content']
    assert len(jobs) + 1 == len(new_jobs)


def test_clone_following_QA_job_as_leading_QA_job(new_project):
    '''
        1. clone job following QA -> leading QA
        2. verified only ["DESIGN", "CROWD_SETTINGS", "PRICE_AND_ROW", "QUALITY_SETTINGS"] will be copied
        3. DESIGN including Ontology
    '''
    api = new_project['job_api']
    team_id = new_project['team_id']
    project_id = new_project['id']
    following_QA_job = new_project['following_QA_job']

    # Get jobs for project and save the jobs number
    res = api.get_job_all(team_id=team_id, project_id=project_id)
    assert res.status_code == 200
    assert res.json_response['message'] == 'success'
    data = res.json_response.get('data')
    jobs = data['content']

    title = f"Leading QA job was copied {faker.zipcode()}"
    copy_payload = {
        "copiedFrom": following_QA_job,
        "appendTo": "project_data_source",
        "teamId": team_id,
        "projectId": project_id,
        "title": title,
        "types": ["DESIGN", "CROWD_SETTINGS", "PRICE_AND_ROW", "QUALITY_SETTINGS"]
    }
    # clone job leading WORK -> leading WORK
    res = api.post_clone_job(team_id=team_id, payload=copy_payload)
    assert res.status_code == 200
    assert res.json_response['message'] == 'success'

    data = res.json_response['data']

    assert data['title'] == title
    assert data['cycleNumber'] == 0
    assert data['flowId'] is not None
    assert data['feedback'] == "DISABLED"
    assert data['type'] == "QA"
    assert data['state'] == "DRAFT"
    assert data['activeStatus'] == "ACTIVE"
    assert data['copiedFrom'] == following_QA_job
    assert data['assignmentLeaseExpiry'] == 1800
    assert data['judgmentsPerRow'] == 1
    assert data['rowsPerPage'] == 5
    assert data['displayContributorName'] is None
    assert data['judgmentModifiable'] is False
    assert data['sendBackOp'] == "NO_OP"
    assert data['maxJudgmentPerContributorEnabled'] is False
    assert data['maxJudgmentPerContributor'] == 0
    assert data['unitSegmentType'] == "UNIT_ONLY"
    assert data['internalSecret'] is not None
    assert data['jobCrowd'] is None
    assert data['parentJobId'] is None

    assert data['payRateType'] is not None
    assert data['invoiceStatisticsType'] == "UNIT_COUNT"
    assert data['allowSelfQa'] is False
    assert data['allowAbandonUnits'] is True

    assert data['unitGroupOption'] == "RETAIN"
    assert data['active'] is True
    assert data['running'] is False

    assert data['multipleJudgment'] is False
    assert data['segmented'] is False
    assert data['appenConnectCrowd'] is False
    assert data['draft'] is True
    time.sleep(5)
    # check jobs for project
    res = api.get_job_all(team_id=team_id, project_id=project_id)
    assert res.status_code == 200
    assert res.json_response['message'] == 'success'

    data = res.json_response.get('data')
    new_jobs = data['content']
    assert len(jobs) + 1 == len(new_jobs)


def test_clone_following_QA_job_as_following_QA_job(new_project):
    '''
        1. clone job following QA -> following QA
        2. verified only ["DESIGN", "CROWD_SETTINGS", "PRICE_AND_ROW", "QUALITY_SETTINGS", "SAMPLING"] will be copied
        3. DESIGN including Ontology
    '''
    api = new_project['job_api']
    team_id = new_project['team_id']
    project_id = new_project['id']
    following_QA_job = new_project['following_QA_job']
    leading_QA_job = new_project['leading_QA_job']

    # Get jobs for project and save the jobs number
    res = api.get_job_all(team_id=team_id, project_id=project_id)
    assert res.status_code == 200
    assert res.json_response['message'] == 'success'
    data = res.json_response.get('data')
    jobs = data['content']
    title = f"Following QA job was copied {faker.zipcode()}"
    copy_payload = {
        "copiedFrom": following_QA_job,
        "appendTo": leading_QA_job,
        "teamId": team_id,
        "projectId": project_id,
        "title": title,
        "types": ["DESIGN", "CROWD_SETTINGS", "PRICE_AND_ROW", "QUALITY_SETTINGS", "SAMPLING"]
    }
    # clone job leading WORK -> leading WORK
    res = api.post_clone_job(team_id=team_id, payload=copy_payload)
    assert res.status_code == 200
    assert res.json_response['message'] == 'success'
    data = res.json_response['data']

    assert data['title'] == title
    assert data['cycleNumber'] == 1
    assert data['flowId'] == leading_QA_job
    assert data['feedback'] == "DISABLED"
    assert data['type'] == "QA"
    assert data['state'] == "DRAFT"
    assert data['activeStatus'] == "ACTIVE"
    assert data['copiedFrom'] == following_QA_job
    assert data['assignmentLeaseExpiry'] == 1800
    assert data['judgmentsPerRow'] == 1
    assert data['rowsPerPage'] == 5
    assert data['displayContributorName'] is None
    assert data['judgmentModifiable'] is False
    assert data['sendBackOp'] == "NO_OP"
    assert data['maxJudgmentPerContributorEnabled'] is False
    assert data['maxJudgmentPerContributor'] == 0
    assert data['unitSegmentType'] == "UNIT_ONLY"
    assert data['internalSecret'] is not None
    assert data['jobCrowd'] is None
    assert data['parentJobId'] is None

    assert data['payRateType'] is not None
    assert data['invoiceStatisticsType'] == "UNIT_COUNT"
    assert data['allowSelfQa'] is False
    assert data['allowAbandonUnits'] is True

    assert data['unitGroupOption'] == "RETAIN"
    assert data['active'] is True
    assert data['running'] is False

    assert data['multipleJudgment'] is False
    assert data['segmented'] is False
    assert data['appenConnectCrowd'] is False
    assert data['draft'] is True
    time.sleep(5)
    # check jobs for project
    res = api.get_job_all(team_id=team_id, project_id=project_id)
    assert res.status_code == 200
    assert res.json_response['message'] == 'success'

    data = res.json_response.get('data')
    new_jobs = data['content']
    assert len(jobs) + 1 == len(new_jobs)


def test_appendable_list_contains_valid_active_job(new_project):
    '''
        1. clonable job list should contains the active leading/following WORK/QA jobs which don't have following job
    '''
    job_api = new_project['job_api']
    team_id = new_project['team_id']
    project_id = new_project['id']

    # prepare step: create a new leading work job
    title1 = f"New QF leading work job {_today} {faker.zipcode()}"
    job_payload = {"title": title1,
                   "teamId": team_id,
                   "projectId": project_id,
                   "type": "WORK",
                   "flowId": '',
                   "templateDisplayNm": "No use template",
                   "templateType": {"index": 1},
                   "cml": {"js": "",
                           "css": "",
                           "cml": "<cml:audio_annotation source-data='{{audio_url}}' name='Annotate the thing' validates='required' />",
                           "instructions": "Test CML API update"},
                   "jobFilter": {
                       "projectId": project_id,
                       "origin": "project_data_source",
                       "schedulerDelay": 24,
                       "schedulerUnit": "HOURS",
                       "sampleRate": 10,
                       "segmental": False,
                       "segmentSampleRate": 100,
                       "filterCriteria": "{}",
                       "filterNum": 0,
                       "minimumSampleUnit": 0
                   }
                   }

    # create a leading work job in new flow
    res = job_api.post_create_job_v2(team_id=team_id, payload=job_payload)
    assert res.status_code == 200
    data = res.json_response['data']
    leading_work_job = data['id']
    assert leading_work_job is not None
    assert data['cycleNumber'] == 0
    assert data['type'] == 'WORK'
    assert data['flowId'] == leading_work_job

    # verify the appendable_list contains the new created leading job
    res = job_api.get_job_appendable_as_collection(team_id=team_id, project_id=project_id)
    assert res.status_code == 200
    data = res.json_response['data']
    assert data is not None and len(data) != 0
    jobs_item = [job for job in data if leading_work_job in job['id']]
    # jobs_item = list(filter(lambda item: leading_work_job in item["id"], data))
    assert len(jobs_item) == 1
    item = jobs_item[0]
    assert item['title'] == title1
    assert item['cycleNumber'] == 0
    assert item['flowId'] == leading_work_job
    assert item['type'] == 'WORK'

    # prepare step 2: create a second job(following QA job) in same flow
    title2 = f"Following QA job was copied {_today} {faker.zipcode()}"
    copy_payload = {
        "copiedFrom": leading_work_job,
        "appendTo": leading_work_job,
        "teamId": team_id,
        "projectId": project_id,
        "title": title2,
        "types": ["DESIGN", "CROWD_SETTINGS", "PRICE_AND_ROW"]
    }
    res = job_api.post_clone_job(team_id=team_id, payload=copy_payload)
    assert res.status_code == 200
    data = res.json_response['data']
    assert data is not None
    second_job_id = data['id']
    assert second_job_id is not None
    assert data['cycleNumber'] == 1
    assert data['flowId'] == leading_work_job
    assert data['type'] == 'QA'

    # verify the appendable_list contains the new created second active job
    # and not contains the first leading job, which contains a following job
    res = job_api.get_job_appendable_as_collection(team_id=team_id, project_id=project_id)
    assert res.status_code == 200
    data = res.json_response['data']
    assert data is not None and len(data) != 0

    jobs_item = [job for job in data if second_job_id in job['id']]
    assert len(jobs_item) == 1
    item = jobs_item[0]
    assert item['title'] == title2
    assert item['cycleNumber'] == 1
    assert item['flowId'] == leading_work_job
    assert item['type'] == 'QA'

    jobs_item = [job for job in data if leading_work_job in job['id']]
    assert len(jobs_item) == 0

    # prepare step 3: create a third job(last following QA job) in same flow
    copy_payload = {
        "copiedFrom": leading_work_job,
        "appendTo": second_job_id,
        "teamId": team_id,
        "projectId": project_id,
        "title": f"Last Following QA job was copied {_today} {faker.zipcode()}",
        "types": ["DESIGN", "CROWD_SETTINGS", "PRICE_AND_ROW"]
    }
    res = job_api.post_clone_job(team_id=team_id, payload=copy_payload)
    assert res.status_code == 200
    data = res.json_response['data']
    assert data is not None
    third_job_id = data['id']
    assert third_job_id is not None
    assert data['cycleNumber'] == 2
    assert data['flowId'] == leading_work_job
    assert data['type'] == 'QA'

    # verify the appendable_list not contains any job in this flow(first leading job, second job, third job)
    res = job_api.get_job_appendable_as_collection(team_id=team_id, project_id=project_id)
    assert res.status_code == 200
    data = res.json_response['data']
    assert data is not None

    jobs_item = [job for job in data if leading_work_job in job['id']]
    assert len(jobs_item) == 0

    jobs_item = [job for job in data if second_job_id in job['id']]
    assert len(jobs_item) == 0

    jobs_item = [job for job in data if third_job_id in job['id']]
    assert len(jobs_item) == 0


def test_appendable_list_not_contains_dc_jobs(new_project):
    '''
    2. clonable job list should not contains the DC WORK/QA jobs
    '''
    job_api = new_project['job_api']
    team_id = new_project['team_id']
    project_id = new_project['id']

    # prepare step: create a new DC work job
    title1 = f"New QF DC work job {_today} {faker.zipcode()}"
    job_payload = {"title": title1,
                   "teamId": team_id,
                   "projectId": project_id,
                   "type": "DATA_COLLECTION",
                   "flowId": '',
                   "templateDisplayNm": "No use template",
                   "templateType": {"index": 1},
                   "cml": {"js": "",
                           "css": "",
                           "cml": ""},
                   "jobFilter": {
                       "projectId": project_id,
                       "origin": "project_data_source",
                       "schedulerDelay": 24,
                       "schedulerUnit": "HOURS",
                       "sampleRate": 10,
                       "segmental": False,
                       "segmentSampleRate": 100,
                       "filterCriteria": "{}",
                       "filterNum": 0,
                       "minimumSampleUnit": 0
                   }
                   }

    # create a new QF DC work job
    res = job_api.post_create_job_v2(team_id=team_id, payload=job_payload)
    assert res.status_code == 200
    data = res.json_response['data']
    DC_work_job = data['id']
    assert DC_work_job is not None
    assert data['cycleNumber'] == 0
    assert data['type'] == 'DATA_COLLECTION'
    assert data['flowId'] == DC_work_job

    # create a new QF DC QA job
    job_payload1 = {**job_payload, "title": f"DC QA job in same flow {_today} {faker.zipcode()}", "type": "DATA_COLLECTION_QA"}
    res = job_api.post_create_job_v2(team_id=team_id, payload=job_payload1)
    assert res.status_code == 200
    data = res.json_response['data']
    DC_QA_job = data['id']
    assert DC_QA_job is not None
    assert data['cycleNumber'] == 0
    assert data['type'] == 'DATA_COLLECTION_QA'
    assert data['flowId'] == DC_QA_job

    # verify the appendable_list not contains the dc work/QA job
    res = job_api.get_job_appendable_as_collection(team_id=team_id, project_id=project_id)
    assert res.status_code == 200
    data = res.json_response['data']
    assert data is not None

    jobs_item = [job for job in data if DC_work_job in job['id']]
    assert len(jobs_item) == 0

    jobs_item = [job for job in data if DC_QA_job in job['id']]
    assert len(jobs_item) == 0


def test_appendable_list_not_contains_deleted_job(new_project):
    '''
    3. clonable job list should not contains the deleted jobs
    '''
    job_api = new_project['job_api']
    team_id = new_project['team_id']
    project_id = new_project['id']

    # prepare step: create a new leading work job
    title1 = f"New QF leading work job {_today} {faker.zipcode()}"
    job_payload = {"title": title1,
                   "teamId": team_id,
                   "projectId": project_id,
                   "type": "WORK",
                   "flowId": '',
                   "templateDisplayNm": "No use template",
                   "templateType": {"index": 1},
                   "cml": {"js": "",
                           "css": "",
                           "cml": "<cml:audio_annotation source-data='{{audio_url}}' name='Annotate the thing' validates='required' />",
                           "instructions": "Test CML API update"},
                   "jobFilter": {
                       "projectId": project_id,
                       "origin": "project_data_source",
                       "schedulerDelay": 24,
                       "schedulerUnit": "HOURS",
                       "sampleRate": 10,
                       "segmental": False,
                       "segmentSampleRate": 100,
                       "filterCriteria": "{}",
                       "filterNum": 0,
                       "minimumSampleUnit": 0
                   }
                   }

    # prepare step: create a leading work job in new flow
    res = job_api.post_create_job_v2(team_id=team_id, payload=job_payload)
    assert res.status_code == 200
    data = res.json_response['data']
    leading_work_job = data['id']
    assert leading_work_job is not None
    assert data['cycleNumber'] == 0
    assert data['type'] == 'WORK'
    assert data['flowId'] == leading_work_job

    # prepare step: delete the job
    res = job_api.post_delete_job_v2(team_id=team_id, project_id=project_id, job_id=leading_work_job)
    assert res.status_code == 200

    # prepare step: check delete success
    job_by_id_payload = {"queryContents": ["jobFilter"]}
    job_by_id_res = job_api.post_job_by_id_v2(team_id=team_id, job_id=leading_work_job, payload=job_by_id_payload)
    assert res.status_code == 200
    assert res.json_response['message'] == 'success'
    data = job_by_id_res.json_response['data']
    assert data['id'] == leading_work_job
    assert data['activeStatus'] == "INACTIVE"

    # verify the appendable_list NOT contains the deleted job
    res = job_api.get_job_appendable_as_collection(team_id=team_id, project_id=project_id)
    assert res.status_code == 200
    data = res.json_response['data']
    assert data is not None
    jobs_item = [job for job in data if leading_work_job in job['id']]
    assert len(jobs_item) == 0

