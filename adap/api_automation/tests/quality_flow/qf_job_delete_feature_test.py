"""
### clone job feature major tests

# delete API
# https://api-kepler.integration.cf3.us/work/swagger-ui/index.html#/job-controller-2/deleteJob
#----- single delete job tests -----
1. can delete leading draft (work/QA) job, and all following jobs both deleted(activeStatus=INACTIVE)
2. can't delete following(second/third) job
3. can't delete DC work/QA job

#----- delete job tests with conditions -----
4. can delete paused job without units
5. can delete paused job without units group
6. can delete paused job with deleted all units
7. can delete paused job with removed all units
8. can't delete paused job with unit
9. can't delete paused job with unit group

10. can delete running job without unit
11. can delete running job without unit group
12. can delete running job with deleted all units
13. can delete running job with removed all units
14. can delete running job with timeout unit
15. can delete running job with timeout unit group
16. can delete running job with abandoned unit
17. can delete running job with abandoned unit group
18. can't delete running job with unit
19. can't delete running job with unit group
20. can't delete running job with submitted unit
21. can't delete running job with submitted unit groups

#----- send unit to delete job tests -----
22. can't assign units(group) to deleted job (should not list the inactive job: https://api-kepler.integration.cf3.us/work/v2/job/list?projectId=ff8b4984-90b4-4898-bf81-7f190cc9fe5d&teamId=acdac212-8e03-49a9-99cb-dd157ccabe29)
23. should not list the inactive job flow in project jobs page (https://api-kepler.integration.cf3.us/work/job/list-as-flow?projectId=ff8b4984-90b4-4898-bf81-7f190cc9fe5d&teamId=acdac212-8e03-49a9-99cb-dd157ccabe29)

#----- sample configuration for delete job tests -----
24. should remove/disable the sample configuration for deleted job flow

#----- assign contributor to delete job tests -----
25. should not list the deleted job in curated crowd page (https://api-kepler.integration.cf3.us/contributor/crowd/criteria-search?teamId=acdac212-8e03-49a9-99cb-dd157ccabe29)
26. should list contributors to deleted job (not list in this query: https://api-kepler.integration.cf3.us/contributor/crowd/batch-detail?teamId=acdac212-8e03-49a9-99cb-dd157ccabe29)
27. should not assign/unassign contributors to deleted job (https://api-kepler.integration.cf3.us/contributor/crowd/assign-job?teamId=acdac212-8e03-49a9-99cb-dd157ccabe29)
28. PROJECT STATISTICS should not calculate the deleted jobs (?? not sure: https://api-kepler.integration.cf3.us/batchjob/progress/statistics?projectId=ff8b4984-90b4-4898-bf81-7f190cc9fe5d&teamId=acdac212-8e03-49a9-99cb-dd157ccabe29)

#----- dashboard metrics for deleted job tests -----
29. should not list the deleted job in dashboard progress: ( https://api-kepler.integration.cf3.us/project/job-statistic/progress?projectId=ff8b4984-90b4-4898-bf81-7f190cc9fe5d&datasetRowType=UNIT&teamId=acdac212-8e03-49a9-99cb-dd157ccabe29)
30. should not list the deleted job in dashboard throughput: ( https://api-kepler.integration.cf3.us/metrics/productivity/job-throughput?teamId=acdac212-8e03-49a9-99cb-dd157ccabe29
31. should not list the deleted job in dashboard quality leading job: ( https://api-kepler.integration.cf3.us/metrics/quality/job-dashboard-category?teamId=acdac212-8e03-49a9-99cb-dd157ccabe29
32. should not list the deleted job in dashboard quality review job: https://api-kepler.integration.cf3.us/metrics/quality/review-job-statistic?teamId=acdac212-8e03-49a9-99cb-dd157ccabe29

#----- Clone function(covered in qf_job_clone_feature_test.py)  -----
33. clonable job list should not contains the deleted jobs (# https://api-kepler.integration.cf3.us/work/job/appendable-as-collection)

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
    upload units
    create a leading work job A1 in flow A
    create a following QA job A2 in flow A
    create a leading QA job B1 in flow B
    check upload units success
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

    # upload units to project dataset
    # TODO

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

    # verify and wait units upload success

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


def new_segmented_project():
    """
    create a new SEGMENTED test project
    upload segmented groups
    create a leading work job A1 in flow A
    create a following QA job A2 in flow A
    create a leading QA job B1 in flow B
    check uploaded unit groups success
    """

    username = get_test_data('qf_user', 'email')
    password = get_test_data('qf_user', 'password')
    team_id = get_user_team_id('qf_user')

    api = QualityFlowApiProject()
    api.get_valid_sid(username, password)

    # create a new SEGMENTED test project
    project_name = f"automation project {_today} {faker.zipcode()}: job clone feature test"
    payload = {"name": project_name,
               "description": project_name,
               "unitSegmentType": "SEGMENTED"}
    res = api.post_create_project(team_id=team_id, payload=payload)
    assert res.status_code == 200
    data = res.json_response.get('data')
    assert data, "Project data has not been found"
    project_id = data['id']

    # upload units to project dataset
    # TODO

    # create test jobs
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

    # verify and wait unit groups upload success
    # TODO

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


def test_delete_leading_draft_qf_work_or_QA_job(new_project):
    '''
    Scenario 1. can delete leading draft (work/QA) job, and all following jobs both deleted(job activeStatus=INACTIVE)
    '''
    pass