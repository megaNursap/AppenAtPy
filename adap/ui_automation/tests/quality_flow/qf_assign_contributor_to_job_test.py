import datetime
import re
import time

import pytest
from faker import Faker

from adap.api_automation.services_config.quality_flow import QualityFlowApiContributor, QualityFlowApiWork, \
    QualityFlowApiProject
from adap.api_automation.utils.data_util import get_test_data, get_user_team_id, get_data_file
from adap.support.generate_test_data.adap.verify_email import verify_user_email_akon
from adap.ui_automation.utils.utils import delete_csv_file
from scripts.one_offs.create_contributors_api import sign_up

faker = Faker()

mark_env = pytest.mark.skipif(not pytest.running_in_preprod_integration, reason="for Integration env")
pytestmark = [pytest.mark.qf_ui,
              pytest.mark.regression_qf,
              pytest.mark.ac_ui_vendor_registration,
              mark_env]
icm_email = "integration+" + faker.zipcode() + '@figure-eight.com'
icm_name = faker.name()
icm_group_name = faker.name()

contributor_email_1 = faker.email()
contributor_name_1 = faker.name()

contributor_email_2 = faker.email()
contributor_name_2 = faker.name()

contributor_email_3 = faker.email()
contributor_name_3 = faker.name()

username = get_test_data('qf_user_ui', 'email')
password = get_test_data('qf_user_ui', 'password')
team_id = get_test_data('qf_user_ui', 'teams')[0]['id']
PASSWORD = get_test_data('test_ui_account', 'password')


@pytest.fixture(scope="module")
def qf_login(app):
    app.user.login_as_customer(username, password)
    app.driver.implicitly_wait(2)


@pytest.fixture(scope="module")
def setup():
    api = QualityFlowApiProject()
    api.get_valid_sid(username, password)

    _today = datetime.datetime.now().strftime("%Y_%m_%d")
    project_name = f"automation project {_today} {faker.zipcode()}: copy job -ui"
    payload = {"name": project_name,
               "description": project_name,
               "unitSegmentType": "UNIT_ONLY"}

    res = api.post_create_project(team_id=team_id, payload=payload)
    assert res.status_code == 200

    response = res.json_response
    data = response.get('data')
    assert data, "Project data has not been found"

    # create Work job
    job_api = QualityFlowApiWork()
    job_api.get_valid_sid(username, password)
    payload = {"title": "New  WORK job",
               "teamId": team_id,
               "projectId": data['id'],
               "type": "WORK",
               "flowId": '',
               "templateDisplayNm": "No use template",
               "templateType": {"index": 1},
               "cml": {"js": "",
                       "css": "",
                       "cml": "<cml:audio_annotation source-data='{{audio_url}}' name='Annotate the thing' validates='required' />",
                       "instructions": "Test CML API update"}
               }

    res = job_api.post_create_job(team_id=team_id, payload=payload)
    assert res.status_code == 200

    # create QA job
    clone_job_payload = {
        "copiedFrom": res.json_response['data']['id'],
        "appendTo": res.json_response['data']['id'],
        "teamId": team_id,
        "projectId": data['id'],
        "title": f"leading job - clone from leading job - {faker.zipcode()}",
        "types": ["DESIGN"]
    }

    res_qa_job = job_api.post_clone_job_v2(team_id, clone_job_payload)
    assert res.json_response["code"] == 200

    return {
        "project_id": data['id'],
        "project_name": project_name,
        "team_id": data['teamId'],
        "work_job_id": res.json_response['data']['id'],
        "work_job_name": 'New  WORK job',
        "qa_job_id": res_qa_job.json_response['data']['id']
    }


@pytest.fixture(scope="module")
def new_contributor(app):
    api = QualityFlowApiContributor()
    api.get_valid_sid(username, password)

    res = api.post_internal_contributor_create(email=icm_email, name=icm_name, team_id=team_id)
    assert res.status_code == 200


@pytest.fixture(scope="module")
def contributors(app):
    api = QualityFlowApiContributor()
    api.get_valid_sid(username, password)

    print("icm_email[1] ", contributor_email_1)
    print("icm_email[2] ", contributor_email_2)
    print("icm_email[3] ", contributor_email_3)
    print("icm_name[1] ", contributor_name_1)
    print("icm_name[2] ", contributor_name_2)
    print("icm_name[3] ", contributor_name_3)

    res_1 = api.post_internal_contributor_create(email=contributor_email_1, name=contributor_name_1, team_id=team_id)
    assert res_1.status_code == 200

    res_2 = api.post_internal_contributor_create(email=contributor_email_2, name=contributor_name_2, team_id=team_id)
    assert res_2.status_code == 200

    res_3 = api.post_internal_contributor_create(email=contributor_email_3, name=contributor_name_3, team_id=team_id)
    assert res_3.status_code == 200

    return {
        "contributor_email_1": contributor_email_1,
        "contributor_name_1": contributor_name_1,
        "contributor_email_2": contributor_email_2,
        "contributor_name_2": contributor_name_2,
        "contributor_email_3": contributor_email_3,
        "contributor_name_3": contributor_name_3
    }


@pytest.fixture(scope="module")
def new_contributor_group(app, contributors):
    api = QualityFlowApiContributor()
    api.get_valid_sid(username, password)

    res_1 = api.post_search_contributor_by_name(name=contributors['contributor_email_1'], team_id=team_id)
    res_2 = api.post_search_contributor_by_name(name=contributors['contributor_email_2'], team_id=team_id)
    res_3 = api.post_search_contributor_by_name(name=contributors['contributor_email_3'], team_id=team_id)

    response_1 = res_1.json_response
    assert res_1.status_code == 200

    response_2 = res_2.json_response
    assert res_2.status_code == 200

    response_3 = res_3.json_response
    assert res_3.status_code == 200

    print("contributor_id_1 ", response_1.get("data").get("list")[0].get("id"))
    print("contributor_id_2 ", response_2.get("data").get("list")[0].get("id"))
    print("contributor_id_3 ", response_3.get("data").get("list")[0].get("id"))

    print("icm_group_name ", icm_group_name)
    print("team_id ", team_id)

    contributor_id_1 = response_1.get("data").get("list")[0].get("id")
    contributor_id_2 = response_2.get("data").get("list")[0].get("id")
    contributor_id_3 = response_3.get("data").get("list")[0].get("id")

    res = api.post_add_multiple_contributors_to_new_group(group_name=icm_group_name,
                                                          contributor_ids=[contributor_id_1, contributor_id_2,
                                                                           contributor_id_3],
                                                          team_id=team_id)
    assert res.status_code == 200

    return {
        "contributor_email_1": contributors['contributor_email_1'],
        "contributor_name_1": contributors['contributor_name_1'],
        "contributor_email_2": contributors['contributor_email_2'],
        "contributor_name_2": contributors['contributor_name_2'],
        "contributor_email_3": contributors['contributor_email_3'],
        "contributor_name_3": contributors['contributor_name_3']
    }


@pytest.fixture(scope="module")
def upload_dataset(setup):
    api = QualityFlowApiProject()
    api.get_valid_sid(username, password)

    project_id = setup['project_id']
    dataset_id = '00000000-0000-0000-0000-000000000000'

    res = api.get_upload_dataset(project_id=project_id, team_id=team_id, dataset_id=dataset_id)
    assert res.status_code == 200
    time.sleep(5)


@pytest.fixture(scope="module")
def send_units_to_job(setup):
    api = QualityFlowApiProject()
    api.get_valid_sid(username, password)

    project_id = setup['project_id']

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
    time.sleep(2)

    unit_id_1 = res.json_response['data']['units'][0]['unitId'][0]['value']
    unit_id_2 = res.json_response['data']['units'][1]['unitId'][0]['value']
    unit_id_3 = res.json_response['data']['units'][2]['unitId'][0]['value']
    unit_id_4 = res.json_response['data']['units'][3]['unitId'][0]['value']

    unit_display_id_1 = res.json_response['data']['units'][0]['unitDisplayId'][0]['value']
    unit_display_id_2 = res.json_response['data']['units'][1]['unitDisplayId'][0]['value']
    unit_display_id_3 = res.json_response['data']['units'][2]['unitDisplayId'][0]['value']
    unit_display_id_4 = res.json_response['data']['units'][3]['unitDisplayId'][0]['value']

    print("unit_id_1 ", unit_id_1)
    print("unit_id_2 ", unit_id_2)
    print("unit_id_3 ", unit_id_3)
    print("unit_id_4 ", unit_id_4)

    print("unit_display_id_1 ", unit_display_id_1)
    print("unit_display_id_2 ", unit_display_id_2)
    print("unit_display_id_3 ", unit_display_id_3)
    print("unit_display_id_4 ", unit_display_id_4)

    res = api.post_job_preview_v2(setup['work_job_id'], team_id)
    assert res.json_response["code"] == 200
    assert res.json_response['message'] == 'success'

    # res = api.post_launch_job_v2(job_id=work_job['job_id'], team_id=team_id)
    # assert res.status_code == 200

    # Send unit to job
    payload = {"projectId": project_id,
               "unitIds": [unit_id_1, unit_id_2, unit_id_3, unit_id_4],
               "percentage": 100,
               "sendEntireGroup": "false",
               "carryJudgment": "true",
               "overwriteJudgment": "true"}
    res = api.post_send_to_job(job_id=setup['work_job_id'], team_id=team_id, payload=payload)
    print("res.json_response ", res.json_response)
    assert res.json_response['code'] == 200
    assert res.json_response['message'] == 'success'
    time.sleep(2)

    return {
        "unit_id_1": unit_display_id_1,
        "unit_id_2": unit_display_id_2,
        "unit_id_3": unit_display_id_3,
        "unit_id_4": unit_display_id_4
    }


@pytest.mark.regression_qf
@pytest.mark.qf_ui_smoke
def test_add_contributor_modal_ui_elements(app, setup, new_contributor, new_contributor_group, qf_login):
    project_id = setup['project_id']
    job_id = setup['work_job_id']

    app.quality_flow.navigate_to_manage_contributor_page_by_project_id_and_job_id(project_id, job_id)
    app.driver.implicitly_wait(5)
    app.quality_flow.job.setting.click_assign_contributor_menu('All Contributors')
    app.quality_flow.job.setting.validate_ui_elements_in_assign_contributor_modal()
    app.quality_flow.job.setting.close_assign_contributor_modal()


@pytest.mark.regression_qf
def test_assign_one_contributor_to_work_job(app, setup, new_contributor, qf_login):
    project_id = setup['project_id']
    job_id = setup['work_job_id']

    app.quality_flow.navigate_to_manage_contributor_page_by_project_id_and_job_id(project_id, job_id)
    app.driver.implicitly_wait(5)
    app.quality_flow.job.setting.click_assign_contributor_menu('All Contributors')

    app.quality_flow.job.setting.select_single_contributor_checkboxes_from_assign_contributor_popup(icm_email)

    app.navigation.click_link('Assign')
    app.verification.text_present_on_page('Assigned Successfully.')
    app.quality_flow.job.setting.validate_the_table_list_contains_contributor(icm_email)


@pytest.mark.regression_qf
def test_assign_one_contributor_to_qa_job(app, setup, new_contributor, qf_login):
    project_id = setup['project_id']
    job_id = setup['qa_job_id']

    app.quality_flow.navigate_to_manage_contributor_page_by_project_id_and_job_id(project_id, job_id)
    app.driver.implicitly_wait(5)
    app.quality_flow.job.setting.click_assign_contributor_menu('All Contributors')

    app.quality_flow.job.setting.select_single_contributor_checkboxes_from_assign_contributor_popup(icm_email)

    app.navigation.click_link('Assign')
    app.verification.text_present_on_page('Assigned Successfully.')
    app.quality_flow.job.setting.validate_the_table_list_contains_contributor(icm_email)


@pytest.mark.regression_qf
def test_assign_multiple_contributors_to_job(app, setup, new_contributor, qf_login):
    project_id = setup['project_id']
    job_id = setup['work_job_id']

    app.quality_flow.navigate_to_manage_contributor_page_by_project_id_and_job_id(project_id, job_id)
    app.driver.implicitly_wait(5)
    app.quality_flow.job.setting.click_assign_contributor_menu('All Contributors')

    contributor_1 = app.quality_flow.job.setting.get_contributor_by_index_from_assign_contributor_popup(1)
    contributor_2 = app.quality_flow.job.setting.get_contributor_by_index_from_assign_contributor_popup(2)
    contributor_3 = app.quality_flow.job.setting.get_contributor_by_index_from_assign_contributor_popup(3)

    app.quality_flow.job.setting.select_multiple_contributor_checkboxes_from_assign_contributor_popup(3)
    app.navigation.click_link('Assign')
    app.verification.text_present_on_page('Assigned Successfully.')

    app.quality_flow.job.setting.validate_the_table_list_contains_contributor(contributor_1)
    app.quality_flow.job.setting.validate_the_table_list_contains_contributor(contributor_2)
    app.quality_flow.job.setting.validate_the_table_list_contains_contributor(contributor_3)


@pytest.mark.regression_qf
def test_assign_multiple_contributors_to_qa_job(app, setup, new_contributor, qf_login):
    project_id = setup['project_id']
    job_id = setup['qa_job_id']

    app.quality_flow.navigate_to_manage_contributor_page_by_project_id_and_job_id(project_id, job_id)
    app.driver.implicitly_wait(5)
    app.quality_flow.job.setting.click_assign_contributor_menu('All Contributors')

    contributor_1 = app.quality_flow.job.setting.get_contributor_by_index_from_assign_contributor_popup(1)
    contributor_2 = app.quality_flow.job.setting.get_contributor_by_index_from_assign_contributor_popup(2)
    contributor_3 = app.quality_flow.job.setting.get_contributor_by_index_from_assign_contributor_popup(3)

    app.quality_flow.job.setting.select_multiple_contributor_checkboxes_from_assign_contributor_popup(3)
    app.navigation.click_link('Assign')
    app.verification.text_present_on_page('Assigned Successfully.')

    app.quality_flow.job.setting.validate_the_table_list_contains_contributor(contributor_1)
    app.quality_flow.job.setting.validate_the_table_list_contains_contributor(contributor_2)
    app.quality_flow.job.setting.validate_the_table_list_contains_contributor(contributor_3)


@pytest.mark.regression_qf
def test_assign_group_contributor_job(app, setup, new_contributor_group, qf_login):
    project_id = setup['project_id']
    job_id = setup['work_job_id']

    app.quality_flow.navigate_to_manage_contributor_page_by_project_id_and_job_id(project_id, job_id)
    app.driver.implicitly_wait(5)
    app.quality_flow.job.setting.click_assign_contributor_menu('Contributor Groups')
    app.quality_flow.job.setting.select_single_contributor_checkboxes_from_assign_contributor_popup(icm_group_name)
    app.navigation.click_link('Assign')
    app.verification.text_present_on_page('Assigned Successfully.')

    app.quality_flow.job.setting.validate_the_table_list_contains_contributor(contributor_email_1)
    app.quality_flow.job.setting.validate_the_table_list_contains_contributor(contributor_email_2)
    app.quality_flow.job.setting.validate_the_table_list_contains_contributor(contributor_email_3)


@pytest.mark.regression_qf
def test_assign_contributors_from_csv_file(app, setup, qf_login):
    project_id = setup['project_id']
    job_id = setup['work_job_id']

    app.quality_flow.navigate_to_manage_contributor_page_by_project_id_and_job_id(project_id, job_id)
    app.driver.implicitly_wait(5)
    csv_data = app.quality_flow.job.setting.generate_contributors_csv()
    app.quality_flow.job.setting.click_assign_contributor_menu('Upload Contributors')

    app.quality_flow.job.setting.upload_contributors_via_csv(csv_data['file_path'])

    app.quality_flow.job.setting.click_assign_contributor_menu('All Contributors')
    app.quality_flow.job.setting.select_single_contributor_checkboxes_from_assign_contributor_popup(csv_data['email1'])
    app.navigation.click_link('Assign')
    app.verification.text_present_on_page('Assigned Successfully.')
    app.quality_flow.job.setting.validate_the_table_list_contains_contributor(csv_data['email1'])

    delete_csv_file(csv_data['file_path'])


@pytest.mark.regression_qf
def test_assign_contributors_from_wrong_email_format_csv(app, setup, qf_login):
    project_id = setup['project_id']
    job_id = setup['work_job_id']

    app.quality_flow.navigate_to_manage_contributor_page_by_project_id_and_job_id(project_id, job_id)
    app.driver.implicitly_wait(5)

    file_name = get_data_file("/internal_contributor/InternalContributorWrongEmailFormat.csv")

    app.quality_flow.job.setting.click_assign_contributor_menu('Upload Contributors')

    app.quality_flow.job.setting.upload_contributors_via_csv(file_name)
    app.verification.text_present_on_page('INVALID')



