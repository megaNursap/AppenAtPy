"""
https://appen.atlassian.net/browse/QED-1962
Get csv ontology report
Get json ontology report
"""

from adap.api_automation.services_config.ontology_management import *
from adap.api_automation.utils.data_util import *
from adap.data import annotation_tools_cml as data
from adap.ui_automation.services_config.annotation import create_annotation_tool_job

mark_env = pytest.mark.skipif(not pytest.running_in_preprod_sandbox, reason="Sandbox enabled feature")
pytestmark = [pytest.mark.ontology_management_api, mark_env, pytest.mark.regression_ontology_attribute, pytest.mark.adap_api_uat]

USER_EMAIL = get_user_email('test_account')
PASSWORD = get_user_password('test_account')
API_KEY = get_user_api_key('test_account')
DATA_FILE = get_data_file("/audio_annotation/audio_data.csv")


@pytest.mark.smoke
@pytest.mark.uat_api
def test_get_csv_ontology_report_for_audio_job():
    job_id = create_annotation_tool_job(API_KEY, DATA_FILE, data.audio_annotation_cml,
                                         job_title="Testing ontology management api", units_per_page=5)
    res = OntologyManagement().upload_csv_ontology_file(job_id, API_KEY, get_data_file("/audio_annotation/ontology.csv"))
    res.assert_response_status(204)
    res = OntologyManagement().get_csv_ontology_report(job_id, API_KEY)
    res.assert_response_status(200)
    assert 'display_color' in str(res.content)
    assert 'description' in str(res.content)
    assert 'class_name' in str(res.content)
    assert '#9A2517' in str(res.content)
    assert 'Name' in str(res.content)
    assert '#C1561A' in str(res.content)
    assert 'Address' in str(res.content)


@pytest.mark.parametrize('case_desc, job_id, api_key, expected_status, error_message',
                         [
                          ("invalid job id", "random_job_id", "api_key", 404, ['There is not an ontology associated with the Job', 'Not Found']),
                          ("missing job id", "", "api_key", 404, ""),
                          ("invalid api key", "job_id", "random_api_key", 403, "Unauthorized token"),
                          ("missing api key", "job_id", "", 403, "Unauthorized token"),
                          ])
def test_get_csv_ontology_report_invalid_data(case_desc, job_id, api_key, expected_status, error_message):
    if api_key == "api_key":
        api_key = API_KEY
    elif api_key == "random_api_key":
        api_key = generate_random_string()
    if job_id == "random_job_id":
        job_id = random.randint(50, 100)
    elif job_id == "job_id":
        job_id = create_annotation_tool_job(API_KEY, DATA_FILE, data.audio_annotation_cml,
                                            job_title="Testing ontology management api", units_per_page=5)
        res = OntologyManagement().upload_csv_ontology_file(job_id, API_KEY,
                                                            get_data_file("/audio_annotation/ontology.csv"))
        res.assert_response_status(204)
    res = OntologyManagement().get_csv_ontology_report(job_id, api_key)
    res.assert_response_status(expected_status)
    if error_message != "":
        assert res.json_response.get('message') in error_message


@pytest.mark.smoke
@pytest.mark.uat_api
def test_get_json_ontology_report_for_audio_job():
    job_id = create_annotation_tool_job(API_KEY, DATA_FILE, data.audio_annotation_cml,
                                        job_title="Testing ontology management api", units_per_page=5)
    res = OntologyManagement().upload_csv_ontology_file(job_id, API_KEY,
                                                        get_data_file("/audio_annotation/ontology.csv"))
    res.assert_response_status(204)
    res = OntologyManagement().get_json_ontology_report(job_id, API_KEY)
    res.assert_response_status(200)
    assert len(res.json_response) == 2
    assert res.json_response[0].get('display_color') in ['#9A2517', '#C1561A']
    assert 'description' in res.json_response[0]
    assert res.json_response[0].get('class_name') in ['Name', 'Address']
    assert res.json_response[1].get('display_color') in ['#9A2517', '#C1561A']
    assert 'description' in res.json_response[1]
    assert res.json_response[1].get('class_name') in ['Name', 'Address']


@pytest.mark.smoke
@pytest.mark.uat_api
def test_get_json_ontology_report_for_shape_job():
    job_id = create_annotation_tool_job(API_KEY, get_data_file("/image_annotation/catdog.csv"), data.image_annotation_cml,
                                        job_title="Testing ontology management api", units_per_page=2)
    payload = [{"description":"","class_name":"cat","display_color":"#FF1744"},{"description":"","class_name":"dog","display_color":"#651FFF"}]
    res = OntologyManagement().upload_json_ontology(job_id, API_KEY, payload)
    res.assert_response_status(204)
    res = OntologyManagement().get_json_ontology_report(job_id, API_KEY)
    res.assert_response_status(200)
    assert len(res.json_response) == 2
    assert res.json_response[0].get('display_color') in ['#FF1744', '#651FFF']
    assert 'description' in res.json_response[0]
    assert res.json_response[0].get('class_name') in ['cat', 'dog']
    assert res.json_response[1].get('display_color') in ['#FF1744', '#651FFF']
    assert 'description' in res.json_response[1]
    assert res.json_response[1].get('class_name') in ['cat', 'dog']


@pytest.mark.parametrize('case_desc, job_id, api_key, expected_status, error_message',
                         [
                          ("invalid job id", "random_job_id", "api_key", 404, ['There is not an ontology associated with the Job', 'Not Found']),
                          ("missing job id", "", "api_key", 404, ""),
                          ("invalid api key", "job_id", "random_api_key", 403, "Unauthorized token"),
                          ("missing api key", "job_id", "", 403, "Unauthorized token"),
                          ])
def test_get_json_ontology_report_invalid_data(case_desc, job_id, api_key, expected_status, error_message):
    if api_key == "api_key":
        api_key = API_KEY
    elif api_key == "random_api_key":
        api_key = generate_random_string()
    if job_id == "random_job_id":
        job_id = random.randint(1, 10)
    elif job_id == "job_id":
        job_id = create_annotation_tool_job(API_KEY, DATA_FILE, data.audio_annotation_cml,
                                            job_title="Testing ontology management api", units_per_page=5)
        res = OntologyManagement().upload_csv_ontology_file(job_id, API_KEY,
                                                            get_data_file("/audio_annotation/ontology.csv"))
        res.assert_response_status(204)
    res = OntologyManagement().get_json_ontology_report(job_id, api_key)
    res.assert_response_status(expected_status)
    if error_message != "":
        assert res.json_response.get('message') in error_message