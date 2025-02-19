"""
https://api-kepler.integration.cf3.us/work/swagger-ui/index.html#
"""
import datetime, re, time, random, pytest, json
from faker import Faker
from adap.api_automation.utils.data_util import get_test_data, get_user_team_id, get_data_file
from adap.api_automation.services_config.quality_flow import get_unit_by_index
from adap.api_automation.services_config.qf_api_logic import QualityFlowApiSingletonManager, DataType, CommitPayloadType

mark_env = pytest.mark.skipif(not pytest.running_in_preprod_integration, reason="for Integration env")

pytestmark = [pytest.mark.qf_api,
              pytest.mark.regression_qf,
              mark_env]

faker = Faker()

_today = datetime.datetime.now().strftime("%Y_%m_%d")


@pytest.fixture(scope="module", autouse=False)
def setup():
    username = get_test_data('qf_user', 'email')
    password = get_test_data('qf_user', 'password')
    default_project = get_test_data('qf_user', 'default_project')
    curated_crowd_subject_api_test = get_test_data('qf_user', 'curated_crowd_subject_api_test')
    team_id = get_user_team_id('qf_user')
    qfm = QualityFlowApiSingletonManager(env=pytest.env)
    qfm.get_singleton_instance()
    qfm.set_env(pytest.env, team_id)
    qfm.logic_set_cookies(cookies=qfm.get_valid_sid(username, password))

    return {
        "username": username,
        "password": password,
        "team_id": team_id,
        "api": qfm,
        "default_project": default_project,
        "curated_crowd_subject_api_test": curated_crowd_subject_api_test
    }


@pytest.fixture(scope="module")
def create_new_project_setup(setup):
    api = setup["api"]
    project_name = f"QF Automation Project {_today} {faker.zipcode()} for job main process Test"
    project_info = api.logic_create_qf_project(project_name, project_name)

    return {
        "project_id": project_info["id"],
        "project_name": project_info["name"]
    }


def test_create_leading_qa_job_and_send_unit_to_job(setup, create_new_project_setup):
    """
    Step 1. Create new QF project and a leading QA job
    Step 2. Upload units
    Step 3. Send unit to job failed
    Step 4. Preview job
    Step 5. Send unit to job success
    Step 6. Resume job
    Step 7. Send unit to job success
    """
    api = setup['api']
    team_id = setup['team_id']
    project_id = create_new_project_setup['project_id']

    # Create job
    res = api.post_create_job_v2(team_id=team_id, payload={
        "title": "leading QA job - job process test",
        "teamId": team_id,
        "projectId": project_id,
        "type": "QA",
        "flowId": '',
        "cml": {"js": "",
                "css": "",
                "cml": '<cml:textarea label="Sample text area:" validates="required" />',
                "instructions": "Test JOB API process"}
    })
    assert res.json_response['code'] == 200
    job_id = res.json_response['data']['id']
    version = res.json_response['data']['version']

    # Upload units to job
    api.logic_pm_upload_units(project_id=project_id, env=pytest.env, round_id=1, csv_file=None,
                              gcc={
                                  'num_rows': 20,
                                  'segmentation': False,
                                  'num_group': 20,
                                  'header_size': 3,
                                  'save_path': None})

    # payload for send unit to job by unit id
    payload = {"startRow": 0, "endRow": 1, "filterModel": {}, "sortModel": [], "queryString": ""}
    res = api.post_units(project_id=project_id, team_id=team_id, payload=payload)
    assert res.json_response['code'] == 200
    unit_1 = res.json_response['data']['units'][0]['unitId'][0]['value']
    unit_2 = res.json_response['data']['units'][1]['unitId'][0]['value']

    payload_1 = {"projectId": project_id, "unitIds": [unit_1], "percentage": 100}
    payload_2 = {"projectId": project_id, "unitIds": [unit_2], "percentage": 100}

    # send unit to job
    res = api.post_send_to_job(job_id=job_id, team_id=team_id, payload=payload_1)
    assert res.json_response['code'] == 3014
    assert res.json_response['message'] == 'Job should not be DRAFT.'
    assert res.json_response['data']['total'] is None
    assert res.json_response['data']['error'] is True
    time.sleep(10)

    # verification
    unit_1 = get_unit_by_index(api, project_id, team_id, 0)
    assert unit_1['jobStatus'][0]['value'] == 'NEW'
    assert 'jobAlias' not in unit_1
    assert 'jobTitle' not in unit_1
    assert 'jobId' not in unit_1

    # preview job
    res = api.post_job_preview_v2(team_id, job_id)
    assert res.json_response["code"] == 200
    assert res.json_response['message'] == 'success'

    # send unit to job
    payload = {"projectId": project_id, "unitIds": [unit_1], "percentage": 100}
    res = api.post_send_to_job(job_id=job_id, team_id=team_id, payload=payload_1)
    assert res.json_response["code"] == 200
    assert res.json_response['message'] == 'success'
    assert res.json_response['data']['error'] is False

    # verification
    for i in range(12):
        res = get_unit_by_index(api, project_id, team_id, 0)
        if res['jobStatus'][0]['value'] == 'JUDGABLE':
            break
        time.sleep(10)
    res = get_unit_by_index(api, project_id, team_id, 0)
    assert res['jobStatus'][0]['value'] == 'JUDGABLE'
    assert job_id in res['jobAlias'][0]['link']
    assert res['jobTitle'][0]['value'] == 'leading QA job - job process test'
    assert res['jobId'][0]['value'] == job_id

    # Resume job
    res = api.post_job_resume_v2(team_id, job_id)
    assert res.json_response["code"] == 200
    assert res.json_response['message'] == 'success'

    # send unit to job
    res = api.post_send_to_job(job_id=job_id, team_id=team_id, payload=payload_2)
    assert res.json_response["code"] == 200
    assert res.json_response['message'] == 'success'
    assert res.json_response['data']['error'] is False

    # verification
    for i in range(10):
        res = get_unit_by_index(api, project_id, team_id, 1)
        if res['jobStatus'][0]['value'] == 'JUDGABLE':
            break
        time.sleep(6)
    res = get_unit_by_index(api, project_id, team_id, 1)
    assert res['jobStatus'][0]['value'] == 'JUDGABLE'
    assert job_id in res['jobAlias'][0]['link']
    assert res['jobTitle'][0]['value'] == 'leading QA job - job process test'
    assert res['jobId'][0]['value'] == job_id


def test_qf_sample_configuration_main_process(setup, create_new_project_setup):
    """
    Step 1. Create new QF project
    Step 2. Add AC sync setting
    Step 3. Create leading work job and following QA job
    Step 4. Link AC sync setting to leading work job
    Step 5. Upload units
    Step 6. Set recursive sample configuration (Every 2 HOURS, 50% sample rate, 1 filterCriteria) to leading work job
    Step 7. Set sample configuration to following QA job (50% sample rate)
    Step 8. Assign 2 contributors to leading work job
    Step 9. Assign units to 2 contributors (4 units for one, 6 units for the other)
    Step 10. Two contributors submit judgments in leading work job
    Step 11. Check the units flowing to following QA job
    """
    api = setup['api']
    team_id = setup['team_id']
    project_id = create_new_project_setup['project_id']
    curated_crowd_subject_api_test = setup['curated_crowd_subject_api_test']
    contributors = curated_crowd_subject_api_test['ac_project_info_1']['Contributors_by_job_type']

    ac_id = curated_crowd_subject_api_test['ac_project_info_1']['AC_Project_ID']
    res = api.logic_curated_crowd_ac_setting_and_syncing(project_id, ac_id, "ALL")
    setting_id = res["setting_id"]

    # create leading work job
    cml = '<cml:textarea label="Sample text area:" validates="required" />'
    instructions = "Test JOB API process"
    work_job_id = api.logic_create_and_launch_leading_job(project_id, "WORK", "WORK job A - job process test",
                                                          cml=cml, instructions=instructions, rows_per_page=6,
                                                          target_job_status="PAUSED", pay_rate_type="DEFAULT",
                                                          job_crowd={"crowdType": ["INTERNAL", "EXTERNAL"], "crowdSubType": "APPEN_CONNECT"})
    qa_job_id = api.logic_create_and_launch_following_job(project_id, work_job_id, "QA job A - job process test",
                                                          target_job_status="PAUSED")

    # link AC project to job
    api.logic_curated_crowd_link_ac_sync_setting_to_job(project_id, work_job_id, setting_id)

    # Upload units
    api.logic_pm_upload_units(project_id=project_id, env=pytest.env, round_id=1, csv_file=None,
                              gcc={
                                  'num_rows': 20,
                                  'segmentation': False,
                                  'num_group': 20,
                                  'header_size': 3,
                                  'save_path': None})

    # get total new units
    res = api.post_units(project_id, team_id, payload={
        "startRow": 0,
        "endRow": 29,
        "filterModel": {
            "jobStatus": {
                "values": ["NEW"],
                "filterType": "set"
            }
        },
        "sortModel": [],
        "queryString": ""
    })
    assert res.json_response['code'] == 200
    total_new_units = res.json_response['data']['totalElements']

    # design sample configuration
    job_id = [work_job_id, qa_job_id]
    for job_cycle_num in range(len(job_id)):
        payload = {
            "id": job_id[job_cycle_num],
            "jobFilter": {
                "projectId": project_id,
                "appliedJobId": job_id[job_cycle_num],
                "origin": "project_data_source" if job_cycle_num == 0 else job_id[job_cycle_num - 1],
                "schedulerDelay": 2 if job_cycle_num == 0 else 0,
                "schedulerUnit": "HOURS",
                "sampleRate": 50,
                "segmentSampleRate": 100,
                "segmental": False,
                "filterCriteria": "{\"jobStatus\":{\"values\":[\"NEW\"],\"filterType\":\"set\"}}",
                "filterNum": 1 if job_cycle_num == 0 else 0,
                "minimumSampleUnit": 0
            }
        }
        res = api.put_update_job_v2(team_id, payload)
        assert res.json_response['code'] == 200
        assert res.json_response['code'] == 200
        time.sleep(5)

        # check job status
        res = api.post_job_by_id_v2(team_id, job_id[job_cycle_num], payload={
            "queryContents": ["jobFilter"]
        })
        assert res.json_response['code'] == 200
        rsp = res.json_response
        assert rsp['data']['jobFilter']['sampleRate'] == 50, \
            "Because the actual sampleRate is inequivalent to the designed sampleRate"
        assert rsp['data']['jobFilter']['filterCriteria'] == "{\"jobStatus\":{\"values\":[\"NEW\"],\"filterType\":\"set\"}}", \
            "Because the actual filterCriteria is inequivalent to the designed filterCriteria"

        # run job
        res = api.post_job_resume_v2(team_id, job_id[job_cycle_num])
        assert res.json_response['code'] == 200

    # check work job status
    MAX_LOOP = 30
    count = 0
    res = api.get_job_summary(team_id, project_id, work_job_id)
    while count < MAX_LOOP and res.json_response['data']['totalUnits'] != int(total_new_units * 50 / 100):
        time.sleep(2)
        res = api.get_job_summary(team_id, project_id, work_job_id)
        count += 1
    rsp = res.json_response
    assert rsp['code'] == 200
    assert rsp['data']['frequency'] == f"Every {2} HOURS"
    assert rsp['data']['totalUnits'] == int(total_new_units * 50 / 100), \
        "Because the actual totalUnits of work job is inequivalent to the totalUnits according to sample configuration"
    total_jobw_units = rsp['data']['totalUnits']

    # assign two contributors to WORK job
    job_contributor_sample_ids = random.sample(contributors["jobType_Work"], 2)
    api.logic_assign_contributor_to_job(project_id, job_contributor_sample_ids, work_job_id)

    res = api.post_units(project_id, team_id, payload={
        "startRow": 0,
        "endRow": total_jobw_units - 1,
        "filterModel": {
            "jobId": {
                "filter": work_job_id,
                "filterType": "text",
                "type": "equals"
            }
        },
        "queryString": "",
        "sortModel": []
    })
    rsp = res.json_response
    assert rsp['code'] == 200
    job_units_ids = [x['unitId'][0]['value'] for x in rsp['data']['units']]
    job_units_1 = random.sample(job_units_ids, int(total_jobw_units * 0.4))
    job_units_2 = [x for x in job_units_ids if x not in job_units_1]

    # assign rows to contributors
    payload = {"projectId": project_id, "unitIds": job_units_1}
    res = api.post_send_to_contributor(contributor_id=job_contributor_sample_ids[0], job_id=work_job_id,
                                       team_id=team_id, payload=payload)
    assert res.json_response['code'] == 200
    payload = {"projectId": project_id, "unitIds": job_units_2}
    res = api.post_send_to_contributor(contributor_id=job_contributor_sample_ids[1], job_id=work_job_id,
                                       team_id=team_id, payload=payload)
    assert res.json_response['code'] == 200

    # distribution fetch and submit
    data, _ = api.logic_distribution_fetch_and_submit(
        job_id=work_job_id,
        worker_id=job_contributor_sample_ids[0],
        working_seconds_per_task_page=0,
        job_type="WORK",
        judgment_keys=["sample_text_area"],
        auto_judgment_source_col_name="audio_name",
        auto_judgment=False,
        judgment={"sample_text_area": f"J - {faker.zipcode()} - {faker.city()}"},
        feedback_result_list=["ACCEPTED", "REJECTED"],
        abandon_percentage=0,
        commit_payload_type=CommitPayloadType.AGG,
        data_type=DataType.Textarea
    )
    assert len(data['distributions']) == 4

    # check qa job status
    time.sleep(5)
    res = api.get_job_summary(team_id, project_id, qa_job_id)
    rsp = res.json_response
    assert rsp['code'] == 200
    assert rsp['data']['totalUnits'] == int(total_jobw_units * 0.4 * 50 / 100), \
        "Because the actual totalUnits of qa job is inequivalent to the totalUnits according to sample configuration"

    data, _ = api.logic_distribution_fetch_and_submit(
        job_id=work_job_id,
        worker_id=job_contributor_sample_ids[1],
        working_seconds_per_task_page=0,
        job_type="WORK",
        judgment_keys=["sample_text_area"],
        auto_judgment_source_col_name="audio_name",
        auto_judgment=False,
        judgment={"sample_text_area": f"J - {faker.zipcode()} - {faker.city()}"},
        feedback_result_list=["ACCEPTED", "REJECTED"],
        abandon_percentage=0,
        commit_payload_type=CommitPayloadType.AGG,
        data_type=DataType.Textarea
    )
    assert len(data['distributions']) == 6

    # check qa job status
    time.sleep(5)
    res = api.get_job_summary(team_id, project_id, qa_job_id)
    rsp = res.json_response
    assert rsp['code'] == 200
    assert rsp['data']['totalUnits'] == int(total_jobw_units * 50 / 100), \
        "Because the actual totalUnits of qa job is inequivalent to the totalUnits according to sample configuration"


def test_leading_job_recursive_sample_configuration(setup, create_new_project_setup):
    """
    Step 1. Create a new project
    Step 2. Add new AC sync setting
    Step 3. Create a new job A
    Step 4. Link AC project to job A
    Step 5. Upload units to QF project
    Step 6. Query data set units
    Step 7. Update job A with recursive sample configuration (Every 2 HOURS, 10 fixed units number, 1 filterCriteria)
    Step 8. Check job A status
    Step 9. Wait until all 10 units are sampled into job A
    Step 10. Create a new job B
    Step 11. Update job B with recursive sample configuration in error
    """
    api = setup['api']
    team_id = setup['team_id']
    project_id = create_new_project_setup['project_id']
    default_project = setup['default_project']

    # add new AC sync setting
    ac_id = default_project['curatedCrowd']['ac_project_info']['AC_Project_ID']
    res = api.logic_curated_crowd_ac_setting_and_syncing(project_id, ac_id, "ALL")
    setting_id = res["setting_id"]

    # create leading work job
    work_job_id = api.logic_create_and_launch_leading_job(project_id, "WORK", "WORK job A - job process test",
                                                          target_job_status="PAUSED")

    # link AC project to job
    api.logic_curated_crowd_link_ac_sync_setting_to_job(project_id, work_job_id, setting_id)

    # Upload units to job
    api.logic_pm_upload_units(project_id=project_id, env=pytest.env, round_id=1, csv_file=None,
                              gcc={
                                  'num_rows': 20,
                                  'segmentation': False,
                                  'num_group': 20,
                                  'header_size': 3,
                                  'save_path': None})

    # get total new units
    res = api.post_units(project_id, team_id, payload={
        "startRow": 0,
        "endRow": 29,
        "filterModel": {
            "jobStatus": {
                "values": ["NEW"],
                "filterType": "set"
            }
        },
        "sortModel": [],
        "queryString": ""
    })
    assert res.json_response['code'] == 200

    # design sample configuration
    payload = {
        "id": work_job_id,
        "jobFilter": {
            "projectId": project_id,
            "appliedJobId": work_job_id,
            "origin": "project_data_source",
            "schedulerDelay": 2,
            "schedulerUnit": "HOURS",
            "fixedUnitNum": 10,
            "segmentSampleRate": 100,
            "segmental": False,
            "filterCriteria": "{\"jobStatus\":{\"values\":[\"NEW\"],\"filterType\":\"set\"}}",
            "filterNum": 1,
            "minimumSampleUnit": 0
        }
    }
    res = api.put_update_job_v2(team_id, payload)
    assert res.json_response['code'] == 200

    # check job status
    res = api.post_job_by_id_v2(team_id, work_job_id, payload={
        "queryContents": ["jobFilter"]
    })
    rsp = res.json_response
    assert rsp['code'] == 200
    assert rsp['data']['jobFilter']['fixedUnitNum'] == 10, \
        "Because the actual fixedUnitNum is inequivalent to the designed fixedUnitNum"
    assert rsp['data']['jobFilter']['filterCriteria'] == "{\"jobStatus\":{\"values\":[\"NEW\"],\"filterType\":\"set\"}}", \
        "Because the actual filterCriteria is inequivalent to the designed filterCriteria"

    MAX_LOOP = 30
    count = 0
    res = api.get_job_summary(team_id, project_id, work_job_id)
    while count < MAX_LOOP and res.json_response['data']['totalUnits'] != 10:
        time.sleep(2)
        res = api.get_job_summary(team_id, project_id, work_job_id)
        count += 1
    rsp = res.json_response
    assert rsp['code'] == 200
    assert rsp['data']['frequency'] == f"Every {2} HOURS"
    assert rsp['data']['totalUnits'] == 10, \
        "Because the actual totalUnits of work job is inequivalent to the totalUnits according to sample configuration"

    # create new job with sample configuration
    new_job_id = api.logic_create_and_launch_leading_job(project_id, "WORK", "WORK job B - job process test",
                                                         target_job_status="PAUSED")

    res = api.put_update_job_v2(team_id, payload={
        "id": new_job_id,
        "jobFilter": {
            "projectId": project_id,
            "appliedJobId": new_job_id,
            "origin": "project_data_source",
            "schedulerDelay": 2,
            "schedulerUnit": "HOURS",
            "fixedUnitNum": 10,
            "segmentSampleRate": 100,
            "segmental": False,
            "filterCriteria": "{\"jobStatus\":{\"values\":[\"NEW\"],\"filterType\":\"set\"}}",
            "filterNum": 1,
            "minimumSampleUnit": 0
        }
    })
    assert res.status_code == 400
    assert res.json_response.get('message') == "Cannot have multiple recursive filter under a project"


def test_change_units_assignment_in_multiple_status(setup, create_new_project_setup):
    """
    Step 1. Create a new project
    Step 2. Add new AC sync setting
    Step 3. Create a new job A
    Step 4. Link AC project to job A
    Step 5. Upload units to QF project
    Step 6. Query data set units
    Step 7. Send top 1 NEW unit to job A
    Step 8. Assign unit to contributor 1
    Step 9. Assign unit to contributor 2
    Step 10. Check units assignment

    """
    api = setup['api']
    team_id = setup['team_id']
    project_id = create_new_project_setup['project_id']
    default_project = setup['default_project']
    contributors = default_project['curatedCrowd']['ac_project_info']['AC_Project_Contributors']

    # add new AC sync setting
    ac_id = default_project['curatedCrowd']['ac_project_info']['AC_Project_ID']
    res = api.logic_curated_crowd_ac_setting_and_syncing(project_id, ac_id, "ALL")
    setting_id = res["setting_id"]

    # create leading work job
    work_job_id = api.logic_create_and_launch_leading_job(project_id, "WORK", "WORK job A - job process test",
                                                          target_job_status="RUNNING", rows_per_page=1,
                                                          pay_rate_type="DEFAULT",
                                                          job_crowd={"crowdType": ["INTERNAL", "EXTERNAL"], "crowdSubType": "APPEN_CONNECT"}
                                                          )

    # link AC project to job
    api.logic_curated_crowd_link_ac_sync_setting_to_job(project_id, work_job_id, setting_id)

    # Upload units
    api.logic_pm_upload_units(project_id=project_id, env=pytest.env, round_id=1, csv_file=None,
                              gcc={
                                  'num_rows': 20,
                                  'segmentation': False,
                                  'num_group': 20,
                                  'header_size': 3,
                                  'save_path': None})

    test_types = [
        'not fetched',
        'fetched but not committed'
    ]

    [contributor_1, contributor_2] = random.sample(contributors["jobType_Work"], 2)
    api.logic_assign_contributor_to_job(project_id, [contributor_1, contributor_2], work_job_id)

    for Type in test_types:
        # Query data set units
        res = api.post_units(project_id=project_id, team_id=team_id, payload={
            "startRow": 0,
            "endRow": 29,
            "filterModel": {
                "jobStatus": {
                    "values": ["NEW"],
                    "filterType": "set"
                }
            },
            "sortModel": [],
            "queryString": ""
        })
        assert res.json_response['code'] == 200
        unit_id = [res.json_response['data']['units'][0]['unitId'][0]['value']]

        # Send unit to job
        payload = {"projectId": project_id, "unitIds": unit_id, "percentage": 100}
        res = api.post_send_to_job(job_id=work_job_id, team_id=team_id, payload=payload)
        assert res.json_response['code'] == 200
        assert res.json_response['message'] == 'success'
        time.sleep(10)

        # Assign unit to contributor
        payload = {"projectId": project_id, "unitIds": unit_id}
        res = api.post_send_to_contributor(contributor_id=contributor_1, job_id=work_job_id,
                                           team_id=team_id, payload=payload)
        assert res.json_response['code'] == 200

        if Type == 'fetched but not committed':
            rsp = api.logic_distribution_polling_fetch(
                job_id=work_job_id,
                worker_id=contributor_1,
                max_polling_times=1,
                interval=0,
                max_duration=1
            )
            data_dist = rsp["dataDist"]

        time.sleep(5)
        payload = {"projectId": project_id, "unitIds": unit_id}
        res = api.post_send_to_contributor(contributor_id=contributor_2, job_id=work_job_id,
                                           team_id=team_id, payload=payload)
        assert res.json_response['code'] == 200

        time.sleep(5)
        # check units assignment
        res = api.post_units(project_id=project_id, team_id=team_id, payload={
            "startRow": 0,
            "endRow": 1,
            "filterModel": {
                "unitId": {
                    "criteria": "equals",
                    "values": unit_id,
                    "filterType": "TEXT"
                }
            },
            "sortModel": [],
            "queryString": ""
        })
        assert res.json_response['code'] == 200
        assert res.json_response['data']['units'][0]['latest.workerId'][0]['value'] == contributor_2


def test_send_unit_to_job_in_draft_or_paused_status_without_sampling_configuration(setup, create_new_project_setup):
    """
    Step 1. Create a new project
    Step 2. Create leading work job A with Draft status
    Step 3. Upload units to QF project
    Step 4. Query data set units
    Step 5. Send units to job A
    Step 6. Preview job with Paused status
    Step 7. Send units to job A
    """
    api = setup['api']
    team_id = setup['team_id']
    project_id = create_new_project_setup['project_id']

    # create leading work job
    work_job_id = api.logic_create_and_launch_leading_job(project_id, "WORK", "WORK job A - job process test",
                                                          target_job_status="DRAFT")

    # Upload units to job
    api.logic_pm_upload_units(project_id=project_id, env=pytest.env, round_id=1, csv_file=None,
                              gcc={
                                  'num_rows': 20,
                                  'segmentation': False,
                                  'num_group': 20,
                                  'header_size': 3,
                                  'save_path': None})

    # send a unit to job
    unit1_id = get_unit_by_index(api, project_id, team_id, 0)['unitId'][0]['value']
    payload = {"projectId": project_id, "percentage": 100, "unitIds": [unit1_id]}
    res = api.post_send_to_job(work_job_id, team_id, payload)
    assert res.json_response['code'] == 3014
    assert res.json_response['message'] == 'Job should launch before send units to contributor.'
    assert res.json_response['data']['total'] is None
    assert res.json_response['data']['error'] is True

    # verification
    unit_data = get_unit_by_index(api, project_id, team_id, 0)
    assert unit_data["jobStatus"][0]["value"] == "NEW"

    # preview job
    res = api.post_job_preview_v2(team_id, work_job_id)
    assert res.json_response["code"] == 200
    assert res.json_response['message'] == 'success'

    # send a unit to job
    res = api.post_send_to_job(work_job_id, team_id, payload)
    assert res.json_response["code"] == 200

    # verification
    count = 0
    while count < 30 and unit_data["jobStatus"][0]["value"] != "JUDGABLE":
        time.sleep(2)
        unit_data = get_unit_by_index(api, project_id, team_id, 0)
        count += 1
    assert unit_data["jobStatus"][0]["value"] == "JUDGABLE"


def test_launch_job_with_sampling_configuration(setup, create_new_project_setup):
    """
    Step 1. Create a new project
    Step 2. Upload units
    Step 3. Create leading work job A with Draft status
    Step 4. Query data set units
    Step 5. Update job A with recursive sample configuration (Every 2 HOURS, 20% sample rate, 1 filterCriteria)
    Step 6. Preview job
    Step 7. Check units sampled into job
    """
    api = setup['api']
    team_id = setup['team_id']
    project_id = create_new_project_setup['project_id']

    # Upload units
    api.logic_pm_upload_units(project_id=project_id, env=pytest.env, round_id=1, csv_file=None,
                              gcc={
                                  'num_rows': 20,
                                  'segmentation': False,
                                  'num_group': 20,
                                  'header_size': 3,
                                  'save_path': None})

    # create leading work job
    work_job_id = api.logic_create_and_launch_leading_job(project_id, "WORK", "WORK job A - job process test",
                                                          target_job_status="DRAFT")

    # get total new units
    res = api.post_units(project_id, team_id, payload={
        "startRow": 0,
        "endRow": 29,
        "filterModel": {
            "jobStatus": {
                "values": ["NEW"],
                "filterType": "set"
            }
        },
        "sortModel": [],
        "queryString": ""
    })
    assert res.json_response['code'] == 200
    total_new_units = res.json_response['data']['totalElements']

    payload = {
        "id": work_job_id,
        "jobFilter": {
            "projectId": project_id,
            "appliedJobId": work_job_id,
            "origin": "project_data_source",
            "schedulerDelay": 2,
            "schedulerUnit": "HOURS",
            "sampleRate": 20,
            "segmentSampleRate": 100,
            "segmental": False,
            "filterCriteria": "{\"jobStatus\":{\"values\":[\"NEW\"],\"filterType\":\"set\"}}",
            "filterNum": 1,
            "minimumSampleUnit": 0
        }
    }
    res = api.put_update_job_v2(team_id, payload)
    assert res.json_response['code'] == 200

    # preview job
    res = api.post_job_preview_v2(team_id, work_job_id)
    assert res.json_response["code"] == 200
    assert res.json_response['message'] == 'success'

    # check job status
    res = api.post_job_by_id_v2(team_id, work_job_id, payload={
        "queryContents": ["jobFilter"]
    })
    assert res.json_response['code'] == 200
    rsp = res.json_response
    assert rsp['data']['jobFilter']['sampleRate'] == 20, \
        "Because the actual sampleRate is inequivalent to the designed sampleRate"
    assert rsp['data']['jobFilter']['filterCriteria'] == "{\"jobStatus\":{\"values\":[\"NEW\"],\"filterType\":\"set\"}}", \
        "Because the actual filterCriteria is inequivalent to the designed filterCriteria"

    MAX_LOOP = 30
    count = 0
    res = api.get_job_summary(team_id, project_id, work_job_id)
    while count < MAX_LOOP and res.json_response['data']['totalUnits'] != int(total_new_units * 20 / 100):
        time.sleep(2)
        res = api.get_job_summary(team_id, project_id, work_job_id)
        count += 1
    rsp = res.json_response
    assert rsp['code'] == 200
    assert rsp['data']['frequency'] == f"Every {2} HOURS"
    assert rsp['data']['totalUnits'] == int(total_new_units * 20 / 100), \
        "Because the actual totalUnits of work job is inequivalent to the totalUnits according to sample configuration"
    total_jobw_units = rsp['data']['totalUnits']

    res = api.post_units(project_id, team_id, payload={
        "startRow": 0,
        "endRow": total_jobw_units - 1,
        "filterModel": {
            "jobId": {
                "filter": work_job_id,
                "filterType": "text",
                "type": "equals"
            }
        },
        "queryString": "",
        "sortModel": []
    })
    rsp = res.json_response
    unit_data = rsp['data']['units']
    assert rsp['code'] == 200
    for unit in unit_data:
        assert unit["jobStatus"][0]["value"] == "JUDGABLE"


@pytest.mark.parametrize('source_job_type', [
    'WORK',
    # 'QA'
])
def test_copy_leading_job_to_new_leading_job(setup, create_new_project_setup, source_job_type):
    """
    Step 1. Create a new project
    Step 2. Create leading work/QA job A
    Step 3. Clone job
    Step 4. Check clone job
    Step 5. Launch the cloned job
    """
    api = setup['api']
    team_id = setup['team_id']
    project_id = create_new_project_setup['project_id']

    # create leading work job
    cml = '<cml:textarea label="Sample text area:" validates="required" />'
    instructions = "Test JOB API process"
    leading_job_id = api.logic_create_and_launch_leading_job(project_id, source_job_type,
                                                             f"{source_job_type} job A - job process test",
                                                             target_job_status="DRAFT", cml=cml,
                                                             instructions=instructions)

    clone_job_payload = {
        "copiedFrom": leading_job_id,
        "appendTo": "project_data_source",
        "teamId": team_id,
        "projectId": project_id,
        "title": f"leading job - clone from leading job - {faker.zipcode()}",
        "types": ["DESIGN", "CROWD_SETTINGS", "PRICE_AND_ROW"]
    }
    res = api.post_clone_job_v2(team_id, clone_job_payload)
    assert res.json_response["code"] == 200
    assert res.json_response["data"]['type'] == source_job_type
    new_leading_job_id = res.json_response["data"]['id']

    res = api.get_job_with_cml(team_id, new_leading_job_id)
    assert res.json_response["code"] == 200
    assert res.json_response["data"]['cml'] == cml
    assert res.json_response["data"]['instructions'] == instructions

    # preview job
    res = api.post_job_preview_v2(team_id, new_leading_job_id)
    assert res.json_response["code"] == 200
    assert res.json_response['message'] == 'success'

    # Resume job
    res = api.post_job_resume_v2(team_id, new_leading_job_id)
    assert res.json_response["code"] == 200
    assert res.json_response['message'] == 'success'


@pytest.mark.parametrize('source_job_type, target_job_type', [
    ('WORK', 'WORK'),
    ('QA', 'WORK')
])
def test_copy_leading_job_to_new_following_qa_job(setup, create_new_project_setup, source_job_type, target_job_type):
    """
    Step 1. Create a new project
    Step 2. Create leading work/QA job A and target WORK job B
    Step 3. Clone job from A to B
    Step 4. Check clone job
    Step 5. Launch the cloned job
    """
    api = setup['api']
    team_id = setup['team_id']
    project_id = create_new_project_setup['project_id']

    # create leading work job
    cml = '<cml:textarea label="Sample text area:" validates="required" />'
    instructions = "Test JOB API process"
    leading_job_id_a = api.logic_create_and_launch_leading_job(project_id, source_job_type,
                                                               f"{source_job_type} job A - job process test",
                                                               target_job_status="DRAFT", cml=cml,
                                                               instructions=instructions)
    leading_job_id_b = api.logic_create_and_launch_leading_job(project_id, source_job_type,
                                                               f"{target_job_type} job B - job process test",
                                                               target_job_status="DRAFT", cml=cml,
                                                               instructions=instructions)

    clone_job_payload = {
        "copiedFrom": leading_job_id_a,
        "appendTo": leading_job_id_b,
        "teamId": team_id,
        "projectId": project_id,
        "title": f"following job - clone from leading job - {faker.zipcode()}",
        "types": ["DESIGN", "CROWD_SETTINGS", "PRICE_AND_ROW"]
    }
    res = api.post_clone_job_v2(team_id, clone_job_payload)
    assert res.json_response["code"] == 200
    assert res.json_response["data"]['type'] == "QA"
    new_following_job_id = res.json_response["data"]['id']

    res = api.get_job_with_cml(team_id, new_following_job_id)
    assert res.json_response["code"] == 200
    assert res.json_response["data"]['cml'] == cml
    assert res.json_response["data"]['instructions'] == instructions

    # preview job
    res = api.post_job_preview_v2(team_id, new_following_job_id)
    assert res.json_response["code"] == 200
    assert res.json_response['message'] == 'success'

    # Resume job
    res = api.post_job_resume_v2(team_id, new_following_job_id)
    assert res.json_response["code"] == 200
    assert res.json_response['message'] == 'success'


def test_copy_following_qa_job_to_new_leading_job(setup, create_new_project_setup):
    """
    Step 1. Create a new project
    Step 2. Create leading work job A and its following QA job B
    Step 3. Clone job from B
    Step 4. Check clone job
    Step 5. Launch the cloned job
    """
    api = setup['api']
    team_id = setup['team_id']
    project_id = create_new_project_setup['project_id']

    # create leading work job
    cml = '<cml:textarea label="Sample text area:" validates="required" />'
    instructions = "Test JOB API process"
    leading_job_id = api.logic_create_and_launch_leading_job(project_id, "WORK",
                                                             f"WORK job A - job process test",
                                                             target_job_status="DRAFT", cml=cml,
                                                             instructions=instructions)
    qa_job_id = api.logic_create_and_launch_following_job(project_id, leading_job_id, "QA job B - job process test",
                                                          target_job_status="DRAFT")

    clone_job_payload = {
        "copiedFrom": qa_job_id,
        "appendTo": "project_data_source",
        "teamId": team_id,
        "projectId": project_id,
        "title": f"leading job - clone from following job - {faker.zipcode()}",
        "types": ["DESIGN", "CROWD_SETTINGS", "PRICE_AND_ROW"]
    }
    res = api.post_clone_job_v2(team_id, clone_job_payload)
    assert res.json_response["code"] == 200
    new_leading_job_id = res.json_response["data"]['id']

    res = api.get_job_with_cml(team_id, new_leading_job_id)
    assert res.json_response["code"] == 200
    assert res.json_response["data"]['cml'] == cml
    assert res.json_response["data"]['instructions'] == instructions

    # preview job
    res = api.post_job_preview_v2(team_id, new_leading_job_id)
    assert res.json_response["code"] == 200
    assert res.json_response['message'] == 'success'

    # Resume job
    res = api.post_job_resume_v2(team_id, new_leading_job_id)
    assert res.json_response["code"] == 200
    assert res.json_response['message'] == 'success'


def test_copy_following_qa_job_to_new_following_qa_job(setup, create_new_project_setup):
    """
    Step 1. Create a new project
    Step 2. Create leading work job A and its following QA job B, and target WORK job C
    Step 3. Clone job from B to C
    Step 4. Check clone job
    Step 5. Launch the cloned job
    """
    api = setup['api']
    team_id = setup['team_id']
    project_id = create_new_project_setup['project_id']

    # create leading work job
    cml = '<cml:textarea label="Sample text area:" validates="required" />'
    instructions = "Test JOB API process"
    leading_job_id_a = api.logic_create_and_launch_leading_job(project_id, "WORK",
                                                             f"WORK job A - job process test",
                                                             target_job_status="DRAFT", cml=cml,
                                                             instructions=instructions)
    qa_job_id = api.logic_create_and_launch_following_job(project_id, leading_job_id_a, "QA job B - job process test",
                                                          target_job_status="DRAFT")
    leading_job_id_b = api.logic_create_and_launch_leading_job(project_id, "WORK",
                                                               f"WORK job C - job process test",
                                                               target_job_status="DRAFT", cml=cml,
                                                               instructions=instructions)

    clone_job_payload = {
        "copiedFrom": qa_job_id,
        "appendTo": leading_job_id_b,
        "teamId": team_id,
        "projectId": project_id,
        "title": f"following job - clone from following job - {faker.zipcode()}",
        "types": ["DESIGN", "CROWD_SETTINGS", "PRICE_AND_ROW", "QUALITY_SETTINGS", "SAMPLING"]
    }
    res = api.post_clone_job_v2(team_id, clone_job_payload)
    assert res.json_response["code"] == 200
    new_leading_job_id = res.json_response["data"]['id']

    res = api.get_job_with_cml(team_id, new_leading_job_id)
    assert res.json_response["code"] == 200
    assert res.json_response["data"]['cml'] == cml
    assert res.json_response["data"]['instructions'] == instructions

    # preview job
    res = api.post_job_preview_v2(team_id, new_leading_job_id)
    assert res.json_response["code"] == 200
    assert res.json_response['message'] == 'success'

    # Resume job
    res = api.post_job_resume_v2(team_id, new_leading_job_id)
    assert res.json_response["code"] == 200
    assert res.json_response['message'] == 'success'


def test_remove_segments_from_job(setup, create_new_project_setup):
    """
    Step 1. create leading work job
    Step 2. upload units
    Step 3. send unit group to job
    Step 4. remove partial units from job
    """
    api = setup['api']
    team_id = setup['team_id']
    project_id = create_new_project_setup['project_id']

    # create leading work job
    cml = '<cml:textarea label="Sample text area:" validates="required" />'
    instructions = "Test JOB API process"
    job_id = api.logic_create_and_launch_leading_job(project_id, "WORK", f"WORK job A - job process test",
                                                     target_job_status="PAUSED", cml=cml, instructions=instructions)

    # Upload units
    api.logic_pm_upload_units(project_id=project_id, env=pytest.env, round_id=1, csv_file=None,
                              gcc={
                                  'num_rows': 20,
                                  'segmentation': True,
                                  'num_group': 4,
                                  'header_size': 3,
                                  'save_path': None})

    payload = {"pageSize": 30, "pageNum": 1, "query": "", "jobId": ""}
    res = api.post_segment_group_list(team_id, project_id, payload)
    assert res.status_code == 200
    rsp = res.json_response
    assert rsp['code'] == 200
    segment_group_id = rsp['data']['content'][0]['segmentGroupId']
    segment_num = rsp['data']['content'][0]['totalSegments']

    # get partial units
    partial_num = 3
    res = api.post_units(project_id, team_id, payload={
        "startRow": 0,
        "endRow": 29,
        "filterModel": {
            "segmentGroupId": {
                "values": [segment_group_id],
                "filterType": "set"
            }
        },
        "queryString": "",
        "sortModel": []
    })
    assert res.status_code == 200
    units_data = res.json_response.get('data').get('units')
    unit_ids = [unit['unitId'][0]['value'] for unit in units_data]
    unit_sample_ids = random.sample(unit_ids, partial_num)

    # send unit group to job
    payload = {
        "projectId": project_id,
        "filterModel": {
            "segmentGroupId": {
                "values": [segment_group_id],
                "filterType": "set"
            }
        },
        "queryString": "",
        "percentage": 100
    }
    res = api.post_send_to_job(job_id, team_id, payload)
    assert res.status_code == 200

    # wait for batchjob and recon
    max_loop = 20
    for i in range(max_loop):
        res = api.post_segment_group_list(team_id, project_id,
                                          payload={"pageSize": 30, "pageNum": 1, "query": "", "jobId": job_id})
        if res.json_response.get('data').get('totalElements') == 1 and \
                res.json_response.get('data').get('content')[0].get('totalSegments') == segment_num:
            break
        else:
            time.sleep(3)

    # check job status
    res = api.post_segment_group_list(team_id, project_id,
                                      payload={"pageSize": 30, "pageNum": 1, "query": "", "jobId": job_id})
    assert res.status_code == 200
    rsp = res.json_response
    assert rsp['data']['content'][0]['totalSegments'] == segment_num
    assert rsp['data']['content'][0]['segmentGroupId'] == segment_group_id
    assert rsp['data']['totalElements'] == 1

    # remove partial units from job
    res = api.post_remove_from_job(team_id, payload={
        "projectId": project_id,
        "unitIds": unit_sample_ids
    }, ignore_conflict='true')
    assert res.status_code == 200

    # wait for batchjob and recon
    max_loop = 20
    for i in range(max_loop):
        res = api.post_segment_group_list(team_id, project_id,
                                          payload={"pageSize": 30, "pageNum": 1, "query": "", "jobId": job_id})
        if res.json_response.get('data').get('content')[0].get('totalSegments') == segment_num - partial_num:
            break
        else:
            time.sleep(3)

    # check job status
    res = api.post_segment_group_list(team_id, project_id,
                                      payload={"pageSize": 30, "pageNum": 1, "query": "", "jobId": job_id})
    assert res.status_code == 200
    rsp = res.json_response
    assert rsp['data']['content'][0]['totalSegments'] == segment_num - partial_num
    assert rsp['data']['content'][0]['segmentGroupId'] == segment_group_id
    assert rsp['data']['totalElements'] == 1
