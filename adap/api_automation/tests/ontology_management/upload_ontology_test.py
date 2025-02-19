"""
https://appen.atlassian.net/browse/QED-1962
Upload csv ontology
Upload json ontology
"""

from adap.api_automation.services_config.ontology_management import *
from adap.api_automation.utils.data_util import *
from adap.data import annotation_tools_cml as data
from adap.ui_automation.services_config.annotation import create_annotation_tool_job

mark_env = pytest.mark.skipif(not pytest.running_in_preprod, reason="Preprod feature")
pytestmark = [pytest.mark.ontology_management_api, mark_env, pytest.mark.regression_ontology_attribute]

USER_EMAIL = get_user_email('test_account')
PASSWORD = get_user_password('test_account')
API_KEY = get_user_api_key('test_account')
DATA_FILE = get_data_file("/audio_annotation/audio_data.csv")
CSV_ONTOLOGY_FILE = get_data_file("/audio_annotation/ontology.csv")
JSON_ONTOLOGY_FILE = get_data_file("/text_annotation/ontology.json")


@pytest.mark.smoke
@pytest.mark.uat_api
@pytest.mark.adap_api_smoke
@pytest.mark.devspace
def test_upload_csv_ontology_to_audio_annotation_job():
    job_id = create_annotation_tool_job(API_KEY, DATA_FILE, data.audio_annotation_cml,
                                        job_title="Testing ontology management api", units_per_page=5)
    res = OntologyManagement().upload_csv_ontology_file(job_id, API_KEY, CSV_ONTOLOGY_FILE)
    res.assert_response_status(204)
    res = OntologyManagement().get_csv_ontology_report(job_id, API_KEY)
    res.assert_response_status(200)
    res = OntologyManagement().get_json_ontology_report(job_id, API_KEY)
    res.assert_response_status(200)
    assert len(res.json_response) == 2
    assert res.json_response[0].get('display_color') in ['#9A2517', '#C1561A']
    assert 'description' in res.json_response[0]
    assert res.json_response[0].get('class_name') in ['Name', 'Address']
    assert res.json_response[1].get('display_color') in ['#9A2517', '#C1561A']
    assert 'description' in res.json_response[1]
    assert res.json_response[1].get('class_name') in ['Name', 'Address']


@pytest.mark.parametrize('case_desc, job_id, api_key, ontology_file, expected_status, error_message',
                         [
                          ("invalid job id", "random_job_id", "api_key", "csv_ontology_file", [404, 400], ['Not Found', 'This type of job does not support ontology']),
                          ("missing job id", "", "api_key", "csv_ontology_file", [404], ""),
                          ("invalid api key", "job_id", "random_api_key", "csv_ontology_file", [403], "Unauthorized token"),
                          ("missing api key", "job_id", "", "csv_ontology_file", [403], "Unauthorized token"),
                          ("invalid ontology file", "job_id", "api_key", get_data_file("/audio_annotation/audio_data.csv"), [400], '"[0].class_name" is required'),
                          ("invalid ontology file format", "job_id", "api_key", get_data_file("/text_annotation/ontology.json"), [400], 'File is corrupt or has wrong filetype. Please upload a proper .csv ontology file.'),
                          ("missing ontology file", "job_id", "api_key", "", [500], "")
                          ])
def test_upload_csv_ontology_with_invalid_data(case_desc, job_id, api_key, ontology_file, expected_status, error_message):
    if api_key == "api_key":
        api_key = API_KEY
    elif api_key == "random_api_key":
        api_key = generate_random_string()
    if ontology_file == "csv_ontology_file":
        ontology_file = CSV_ONTOLOGY_FILE
    if job_id == "random_job_id":
        job_id = random.randint(1, 10)
    elif job_id == "job_id":
        job_id = create_annotation_tool_job(API_KEY, DATA_FILE, data.audio_annotation_cml,
                                            job_title="Testing ontology management api", units_per_page=5)
    res = OntologyManagement().upload_csv_ontology_file(job_id, api_key, ontology_file)
    assert res.status_code in expected_status
    if error_message != "":
        assert res.json_response.get('message') in error_message


# right now, csv ontology is not supported by image segmentation,shapes, text annotation, lidar
@pytest.mark.adap_api_smoke
@pytest.mark.devspace
def test_upload_csv_ontology_with_unsupported_job_type():
    job_id = create_annotation_tool_job(API_KEY, get_data_file("/text_annotation/multiplelinesdata.csv"), data.text_annotation_cml,
                                        job_title="Create text annotation job not support csv ontology", units_per_page=5)
    res = OntologyManagement().upload_csv_ontology_file(job_id, API_KEY, CSV_ONTOLOGY_FILE)
    res.assert_response_status(400)
    assert res.json_response.get('message') == 'This type of job does not support csv ontology'


@allure.issue("https://appen.atlassian.net/browse/AT-5140", "BUG: AT-5140")
@pytest.mark.smoke
@pytest.mark.uat_api
@pytest.mark.adap_api_smoke
@pytest.mark.devspace
def test_upload_csv_ontology_report_for_shape_job():
    job_id = create_annotation_tool_job(API_KEY, get_data_file("/image_annotation/catdog.csv"), data.image_annotation_cml,
                                         job_title="Testing ontology management api", units_per_page=2)
    res = OntologyManagement().upload_csv_ontology_file(job_id, API_KEY, get_data_file("/audio_annotation/ontology.csv"))
    res.assert_response_status(400)
    assert res.json_response.get("message") == "This type of job does not support csv ontology"


@pytest.mark.smoke
@pytest.mark.uat_api
@pytest.mark.adap_api_smoke
@pytest.mark.devspace
def test_upload_json_ontology_to_job():
    job_id = create_annotation_tool_job(API_KEY, get_data_file("/text_annotation/multiplelinesdata.csv"),
                                        data.text_annotation_cml,
                                        job_title="Create text annotation job to test upload json ontology",
                                        units_per_page=5)
    payload = [{
                "description": "This is a bus",
                "class_name": "Bus",
                "display_color": "#000000",
                "children": [
                        {
                            "description": "Children of the bus class",
                            "class_name": "children",
                            "display_color": "#ca03fc"
                        }
                    ]
              },
              {
                "description": "This is a Car",
                "class_name": "Car",
                "display_color": "#00008e"
              }]
    res = OntologyManagement().upload_json_ontology(job_id, API_KEY, payload)
    res.assert_response_status(204)
    res = OntologyManagement().get_json_ontology_report(job_id, API_KEY)
    res.assert_response_status(200)
    assert len(res.json_response) == 2
    assert res.json_response[0].get('display_color') in ['#000000', '#00008e']
    assert res.json_response[0].get('description') in ['This is a bus', 'This is a Car']
    assert res.json_response[0].get('class_name') in ['Bus', 'Car']
    assert res.json_response[1].get('display_color') in ['#000000', '#00008e']
    assert res.json_response[1].get('description') in ['This is a bus', 'This is a Car']
    assert res.json_response[1].get('class_name') in ['Bus', 'Car']


def test_upload_nested_json_ontology_to_video_annotation_job():
    for cml in [data.video_annotation_linear_interpolation_cml, data.video_annotation_object_tracking_cml]:
        job_id = create_annotation_tool_job(API_KEY, get_data_file("/video_annotation/video_withoutannotation.csv"), cml,
                                            job_title="Create video annotation job to test upload nested json ontology",
                                            units_per_page=5)
        payload = [{"description":"","class_name":"Nest1","is_folder": True,"children":[{"description":"Don't include bags, strollers, etc.","class_name":"Nest2","is_folder":True,"children":[{"description":"","class_name":"Nest3","is_folder":True,"questions":[],"children":[{"description":"","class_name":"Nest4","display_color":"#651FFF","questions":[]}]}],"relationship_types":[]}],"relationship_types":[]}]
        res = OntologyManagement().upload_json_ontology(job_id, API_KEY, payload)
        res.assert_response_status(204)
        res = OntologyManagement().get_json_ontology_report(job_id, API_KEY)
        res.assert_response_status(200)
        assert len(res.json_response) == 1
        assert res.json_response[0].get('class_name') == "Nest1"
        assert res.json_response[0].get('children')[0].get('class_name') == "Nest2"
        assert res.json_response[0].get('children')[0].get('description') == "Don't include bags, strollers, etc."
        assert res.json_response[0].get('children')[0].get('children')[0].get('class_name') == "Nest3"
        assert res.json_response[0].get('children')[0].get('children')[0].get('children')[0].get('class_name') == "Nest4"
        assert res.json_response[0].get('children')[0].get('children')[0].get('children')[0].get('display_color') == "#651FFF"


def test_upload_csv_ontology_to_ontology_attribute_enabled_or_disabled_job():
    for key in [API_KEY]:
        job_id = create_annotation_tool_job(key, get_data_file("/video_annotation/video_withoutannotation.csv"), data.video_annotation_object_tracking_cml,
                                            job_title="Testing ontology management api", units_per_page=5)
        res = OntologyManagement().upload_csv_ontology_file(job_id, API_KEY, get_data_file("/video_annotation/ontology.json"))
        res.assert_response_status(204)
        res = OntologyManagement().get_csv_ontology_report(job_id, API_KEY)
        res.assert_response_status(200)


@pytest.mark.parametrize('case_desc, job_id, api_key, description, class_name, '
                         'display_color, expected_status, error_message',
                         [
                          ("invalid job id", "random_job_id", "api_key", "This is bus", "Bus", "#000000", [404, 400], ['Not Found', 'This type of job does not support ontology']),
                          ("missing job id", "", "api_key", "This is bus", "Bus", "#000000", [404], ""),
                          ("invalid api key", "job_id", "random_api_key", "This is bus", "Bus", "#000000", [403], "Unauthorized token"),
                          ("missing api key", "job_id", "", "This is bus", "Bus", "#000000", [403], "Unauthorized token"),
                          ("ontology missing required fields", "job_id", "api_key", "", "", "", [400], '"[0].class_name" is not allowed to be empty')
                          ])
def test_upload_json_ontology_with_invalid_data(case_desc, job_id, api_key, description, class_name, display_color, expected_status, error_message):
    if api_key == "api_key":
        api_key = API_KEY
    elif api_key == "random_api_key":
        api_key = generate_random_string()
    if job_id == "random_job_id":
        job_id = random.randint(1, 10)
    elif job_id == "job_id":
        job_id = create_annotation_tool_job(API_KEY, get_data_file("/text_annotation/multiplelinesdata.csv"),
                                            data.text_annotation_cml,
                                            job_title="Create text annotation job to test upload json ontology",
                                            units_per_page=5)

    payload = [{
        "description": description,
        "class_name": class_name,
        "display_color": display_color,
        }]

    res = OntologyManagement().upload_json_ontology(job_id, api_key, payload)
    assert res.status_code in expected_status
    if error_message != "":
        assert res.json_response.get('message') in error_message


# right now, json ontology is not supported by audio annotation, audio transcription,
# pixel labeling, video shapes, video bounding box
def test_upload_json_ontology_with_unsupported_job_type():
    job_id = create_annotation_tool_job(API_KEY, DATA_FILE, data.audio_annotation_cml,
                                        job_title="Testing ontology management api", units_per_page=5)
    payload = [{
            "description": "This is a Car",
            "class_name": "car",
            "display_color": "#00008e"
              }]
    res = OntologyManagement().upload_json_ontology(job_id, API_KEY, payload)
    res.assert_response_status(400)
    assert res.json_response.get('message') == 'This type of job does not support json ontology'