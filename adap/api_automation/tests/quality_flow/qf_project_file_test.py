"""
swagger - https://api-kepler.sandbox.cf3.us/project/swagger-ui/index.html#/Project%20Controller
"""
import time

import requests

from adap.api_automation.services_config.quality_flow import QualityFlowApiProject
import pytest
import datetime
from faker import Faker
from adap.api_automation.utils.data_util import get_test_data, get_user_team_id, get_data_file, \
    find_dict_in_array_by_value
from adap.api_automation.utils.http_util import HttpMethod
from adap.perf_platform.utils.logging import get_logger


LOGGER = get_logger(__name__)

mark_env = pytest.mark.skipif(not pytest.running_in_preprod_integration, reason="for Integration env")

pytestmark = [pytest.mark.qf_api,
              pytest.mark.regression_qf,
              mark_env]

faker = Faker()

_today = datetime.datetime.now().strftime("%Y_%m_%d")


@pytest.fixture(scope="module")
def setup():
    username = get_test_data('qf_user', 'email')
    password = get_test_data('qf_user', 'password')
    default_project = get_test_data('qf_user', 'default_project')
    team_id = get_user_team_id('qf_user')
    api = QualityFlowApiProject()
    api.get_valid_sid(username,password)
    return {
        "username": username,
        "password": password,
        "team_id": team_id,
        "api": api,
        "default_project": default_project
    }


@pytest.fixture(scope="module")
def new_project(setup):
    api = setup['api']
    team_id = setup['team_id']

    project_name = f"automation project {_today} {faker.zipcode()}: files testing "
    payload = {"name": project_name,
               "description": project_name,
               "unitSegmentType": "UNIT_ONLY"}

    res = api.post_create_project(team_id=team_id, payload=payload)
    assert res.status_code == 200

    response = res.json_response
    data = response.get('data')
    assert data, "Project data has not been found"

    return {
        "id": data['id'],
        "team_id": data['teamId'],
        "version": data['version']
    }

#  --------- POST /file/notify   --------------------------
def test_post_file_notify_invalid_cookies(setup):
    api = QualityFlowApiProject()
    team_id = setup['team_id']
    project_id = setup['default_project']['id']
    publish = True
    ignore_warning = False

    payload = {"id": "0c01248c-2d9d-45d6-bd7c-f34a719df557",
               "projectId": project_id,
               "version": 0,
                "result": "success"
               }

    res = api.post_notify_file(team_id=team_id, publish=publish, ignore_warning=ignore_warning, payload=payload)
    assert res.status_code == 401
    assert res.json_response['message'] == 'Please login'


def test_post_file_notify(setup, new_project):
    api = setup['api']
    team_id = setup['team_id']
    project_id = new_project['id']

    sample_file = get_data_file('/units/catdog.csv')
    with open(sample_file, 'r', encoding='utf-8-sig') as f:
        csv_data = f.read()

    res = api.get_file_upload_url(project_id=project_id, team_id=team_id, file_name=sample_file)
    assert res.status_code == 200

    data_id = res.json_response['data']['id']
    presigned_url = res.json_response['data']['presignedUrl']

    time.sleep(3)

    base_url_bak, api.service.base_url = api.service.base_url, ''
    headers = {
        "accept": "*/*",
        "content-type": "text/csv"
    }
    api.service.put(presigned_url, headers=headers, data=csv_data.encode('utf-8'))
    api.service.base_url = base_url_bak

    payload = {"id": data_id,
               "projectId": project_id,
               "version": 0,
                "result": "success"
               }

    res = api.post_notify_file(team_id=team_id, publish=True, ignore_warning=False, payload=payload)
    assert res.status_code == 200

    response = res.json_response
    assert response['message'] == 'success'

    data = response['data']
    assert data, 'Data has not been found'
    assert data['projectId'] == project_id
    assert data['id'] == data_id
    assert data['uploadFileName'] == sample_file
    assert data['status'] == "PUBLISH_READY"
    assert data['filePath'], "filePath has not been found"

    res = api.get_list_of_files_for_project(project_id=project_id, team_id=team_id)
    assert res.status_code == 200
    assert res.json_response['message'] == 'success'

    content = res.json_response['data']['content']
    assert len(content) > 0, "Uploaded files have not been found"

    uploaded_file = find_dict_in_array_by_value(content, 'id',  data_id)
    assert uploaded_file, f"Uploaded file with id {data_id} has not been found"
    assert uploaded_file['id'] == data_id
    assert uploaded_file['status'] == "PUBLISH_READY"
    assert uploaded_file['uploadFileName'] == sample_file
#  --------- GET /files   -----------------------------------

def test_get_projects_files_invalid_cookies(setup):
    api = QualityFlowApiProject()
    team_id = setup['team_id']
    project_id = setup['default_project']['id']

    res = api.get_list_of_files_for_project(project_id=project_id, team_id=team_id)
    assert res.status_code == 401
    assert res.json_response['message'] == 'Please login'


@pytest.mark.parametrize('name, team_id, message', [
    ('empty', '', 'Unauthorized'),
    ('not exist', 'fkreek0mvml','Access Denied'),
    ('other user', '45f42748-482b-4265-8a8c-73efa872b32b', 'Access Denied')
])
def test_get_projects_files_invalid_team_id(setup, name, team_id, message):
    api = setup['api']
    project_id = setup['default_project']['id']
    res = api.get_list_of_files_for_project(project_id=project_id, team_id=team_id)
    assert res.status_code == 203
    assert res.json_response['message'] == message


@pytest.mark.parametrize('name, project_id', [
    ('empty', ''),
    ('not exist', 1000000),
    ('other user', "78a7d0af-1c4f-4ace-9cfd-5e34aa450dac")
])
def test_get_projects_files_invalid_project_id(setup, name, project_id):
    api = setup['api']
    team_id = setup['team_id']

    res = api.get_list_of_files_for_project(project_id=project_id, team_id=team_id)
    assert res.status_code == 203
    assert res.json_response['message'] == 'Unauthorized'


def test_get_projects_files_valid(setup):
    api = setup['api']
    team_id = setup['team_id']
    project_id = setup['default_project']['id']

    res = api.get_list_of_files_for_project(project_id=project_id, team_id=team_id)
    assert res.status_code == 200

    response = res.json_response
    assert response.get('message', False) == 'success'

    data = response.get('data')
    assert data['content'], "Content has not been found"

    file_info = find_dict_in_array_by_value(data['content'], 'uploadFileName', 'authors_add.csv')
    assert file_info, 'File has not been found'
    assert file_info['projectId'] == project_id
    assert file_info['status'] == "UPLOADING"



#  --------- GET /file/upload-url   --------------------------
def test_get_upload_url_invalid_cookies(setup):
    api = QualityFlowApiProject()
    team_id = setup['team_id']
    project_id = setup['default_project']['id']
    sample_file = get_data_file('/authors.csv')

    res = api.get_file_upload_url(project_id=project_id, team_id=team_id, file_name=sample_file)
    assert res.status_code == 401
    assert res.json_response['message'] == 'Please login'


@pytest.mark.parametrize('name, team_id, message', [
    ('empty', '', 'Unauthorized'),
    ('not exist', 'fkreek0mvml', 'Access Denied'),
    ('other user', '45f42748-482b-4265-8a8c-73efa872b32b', 'Access Denied')
])
def test_get_upload_url_invalid_team_id(setup, name, team_id, message):
    api = setup['api']
    project_id = setup['default_project']['id']
    sample_file = get_data_file('/authors.csv')

    res = api.get_file_upload_url(project_id=project_id, team_id=team_id, file_name=sample_file)
    assert res.status_code == 203
    assert res.json_response['message'] == message


@pytest.mark.parametrize('name, project_id', [
    ('empty', ''),
    ('not exist', 1000000),
    ('other user', "78a7d0af-1c4f-4ace-9cfd-5e34aa450dac")
])
def test_get_upload_url_invalid_project_id(setup, name, project_id):
    api = setup['api']
    team_id = setup['team_id']
    sample_file = get_data_file('/authors.csv')

    res = api.get_file_upload_url(project_id=project_id, team_id=team_id, file_name=sample_file)
    assert res.status_code == 203
    assert res.json_response['message'] == 'Unauthorized'


# TODO invalid files

def test_get_upload_url_valid(setup, new_project):
    api = setup['api']
    team_id = setup['team_id']
    project_id = new_project['id']
    sample_file = get_data_file('/authors.csv')

    res = api.get_file_upload_url(project_id=project_id, team_id=team_id, file_name=sample_file)
    assert res.status_code == 200

    response = res.json_response
    assert response['message'] == 'success'

    data = response['data']
    assert data, 'Data has not been found'
    assert data['projectId'] == project_id
    assert data['id'], "Id has not been found"
    assert data['uploadFileName'] == sample_file
    assert data['status'] == "UPLOADING"
    assert data['filePath'], "filePath has not been found"
    assert data['presignedUrl'], "presignedUrl has not been found"


# ----------Upload csv file main process------------------------
def test_csv_file_upload_to_dataset(setup, new_project):
    api = setup['api']
    team_id = setup['team_id']
    project_id = new_project['id']
    audio_csv_file = get_data_file('/authors.csv')
    initial_res_data_summary = api.get_project_data_summary(project_id, team_id)
    unit_number_of_csv_file = int(initial_res_data_summary.json_response["data"]["totalUnits"]) + 5

    units_header = ['Unit ID', 'Status', 'source File Batch Number', 'row Number', 'created At', 'unit Segment Type', 'countries_active', 'author', 'image_url',  'major_works']
    with open(audio_csv_file, 'r', encoding='utf-8-sig') as f:
        csv_data = f.read()

    res = api.get_file_upload_url(project_id, team_id, audio_csv_file)
    S3_url = res.json_response["data"]["presignedUrl"]
    id = res.json_response["data"]["id"]
    base_url_bak, api.service.base_url = api.service.base_url, ''
    headers = {
        "accept": "*/*",
        "content-type": "text/csv"
    }
    api.service.put(S3_url, headers=headers, data=csv_data.encode('utf-8'))
    api.service.base_url = base_url_bak

    res = api.post_notify_file(team_id, publish=True, payload={
        "id": id,
        "projectId": project_id,
        "result": "success",
        "version": 0
    }, ignore_warning=False)
    if res.json_response['code'] == 3007:
        res = api.post_notify_file(team_id, publish=True, payload={
            "id": id,
            "message": "",
            "projectId": project_id,
            "result": "success",
            "statusCode": "200",
            "version": 0
        }, ignore_warning=True)

    MAX_LOOP = 80
    count = 0
    res_files = api.get_list_of_files_for_project(project_id, team_id, page_num=0, page_size=1)
    res_units_header = api.get_units_header(team_id, project_id)
    res_field_values = api.post_field_values(team_id, project_id, payload=["jobStatus"])
    res_data_summary = api.get_project_data_summary(project_id, team_id)
    while count < MAX_LOOP and (res_files.json_response["data"]["content"][0]["status"] != "PUBLISHED" or len(res_units_header.json_response["data"]["columnDefs"]) != 2 or res_field_values.json_response["data"]["values"]["jobStatus"] != ["NEW", ""] or res_data_summary.json_response["data"]["totalUnits"] != unit_number_of_csv_file):
        time.sleep(2)
        res_files = api.get_list_of_files_for_project(project_id, team_id, page_num=0, page_size=1)
        res_units_header = api.get_units_header(team_id, project_id)
        res_field_values = api.post_field_values(team_id, project_id, payload=["jobStatus"])
        res_data_summary = api.get_project_data_summary(project_id, team_id)
        count += 1

    assert res_files.json_response["data"]["content"][0]["status"] == "PUBLISHED"
    assert res_units_header.json_response["data"]["columnDefs"][0]["headerName"] == "unit"
    assert res_units_header.json_response["data"]["columnDefs"][1]["headerName"] == "source"
    unit_header_name = res_units_header.json_response["data"]["columnDefs"][0]["children"]
    source_header_name = res_units_header.json_response["data"]["columnDefs"][1]["children"]

    LOGGER.info(f'source_header_name: {source_header_name}')
    LOGGER.info(f'units_header: {units_header}')

    for i in range(9):
        if i <= 5:
            assert unit_header_name[i]["displayName"] == units_header[i]
        else:
            assert source_header_name[i-6]["displayName"] == units_header[i]

    assert res_field_values.json_response["data"]["values"]["jobStatus"] == ["NEW", ""]
    assert res_data_summary.json_response["data"]["totalUnits"] == unit_number_of_csv_file
    assert res_data_summary.json_response["data"]["newUnits"] == unit_number_of_csv_file

    res = api.get_list_of_downloaded_files(project_id, team_id, data_type="DATA_SET")
    assert res.json_response["message"] == "success"

    res = api.post_units(project_id, team_id, payload={
        "startRow": 0,
        "endRow": 29,
        "filterModel": {},
        "sortModel": [],
        "queryString": ""
    })
    assert res.json_response["data"]["totalElements"] == unit_number_of_csv_file


#  --------- GET /file/download/list   --------------------------
def test_get_download_list_invalid_cookies(setup):
    api = QualityFlowApiProject()
    team_id = setup['team_id']
    project_id = setup['default_project']['id']
    list_type ='JOB_REPORT'

    res = api.get_list_of_downloaded_files(project_id=project_id, team_id=team_id, data_type=list_type)
    assert res.status_code == 401
    assert res.json_response['message'] == 'Please login'


@pytest.mark.parametrize('name, team_id, message', [
    ('empty', '', 'Unauthorized'),
    ('not exist', 'fkreek0mvml', 'Access Denied'),
    ('other user', '45f42748-482b-4265-8a8c-73efa872b32b', 'Access Denied')
])
def test_get_download_list_invalid_team_id(setup, name, team_id, message):
    api = setup['api']
    project_id = setup['default_project']['id']
    list_type = 'JOB_REPORT'

    res = api.get_list_of_downloaded_files(project_id=project_id, team_id=team_id, data_type=list_type)
    assert res.status_code == 203
    assert res.json_response['message'] == message


@pytest.mark.parametrize('data_type', [
   "DATA_SET", "DATA_GROUP", "JOB_REPORT", "JOB_DAILY", "CONTRIBUTOR_DAILY"
])
def test_get_download_list_data_types(setup, data_type):
    api = setup['api']
    project_id = setup['default_project']['id']
    team_id = setup['team_id']

    res = api.get_list_of_downloaded_files(project_id=project_id, team_id=team_id, data_type=data_type)
    assert res.status_code == 200
    assert res.json_response['message'] == 'success'

#     TODO add more functional tests for /file/download/list


#  --------- POST /file/download   --------------------------
def test_project_file_download_invalid_cookies(setup):
    api = QualityFlowApiProject()
    team_id = setup['team_id']
    project_id = setup['default_project']['id']

    body_data = {
        "projectId": project_id,
        "filterModel": {},
        "queryString": "",
        "type": "DATA_SET"
    }

    res = api.post_download_file(team_id, body_data)
    assert res.status_code == 401
    assert res.json_response['message'] == 'Please login'


@pytest.mark.parametrize('name, team_id, message', [
    ('empty', '', 'Unauthorized'),
    ('not exist', 'fkreek0mvml', 'Access Denied'),
    ('other user', '45f42748-482b-4265-8a8c-73efa872b32b', 'Access Denied')
])
def test_project_file_download_invalid_team_id(setup, name, team_id, message):
    api = setup['api']
    project_id = setup['default_project']['id']

    body_data = {
        "projectId": project_id,
        "filterModel": {},
        "queryString": "",
        "type": "DATA_SET"
    }

    res = api.post_download_file(team_id, body_data)
    assert res.status_code == 203
    assert res.json_response['message'] == message


def test_project_file_download_process(setup, new_project):
    api = setup['api']
    project_id = new_project['id']
    team_id = setup['team_id']

    body_data = {
        "projectId": project_id,
        "filterModel": {},
        "queryString": "",
        "type": "DATA_SET"
    }
    res = api.post_download_file(team_id, body_data)
    assert res.json_response['data']['status'] == 'DOWNLOAD_PREPARE'

    start_time = datetime.datetime.now()
    download_URL = None
    MAX_LOOP = 60
    count = 0
    while count < MAX_LOOP:
        count += 1
        res = api.get_list_of_downloaded_files(project_id, team_id, "DATA_SET")
        if res.json_response['data']['status'] == 'DOWNLOAD_READY':
            download_URL = res.json_response['data']['filePath']
            break
        time.sleep(1)
    end_time = datetime.datetime.now()
    print(f'Download cost %.3f seconds' % (end_time - start_time).seconds)
    assert download_URL, 'download_URL has not been found'
    res = requests.get(download_URL)
    assert res.status_code == 200



#  --------- DELETE  /file  --------------------------
def test_delete_file_project_invalid_cookies(setup):
    api = QualityFlowApiProject()
    team_id = setup['team_id']
    project_id = setup['default_project']['id']

    res = api.delete_file(team_id=team_id, project_id=project_id, version=0, id="742f0fab-8e9a-4cef-a154-36b2ae08c398")
    assert res.status_code == 401
    assert res.json_response['message'] == 'Please login'


@pytest.mark.parametrize('name, team_id, message', [
    ('empty', '', 'Unauthorized'),
    ('not exist', 'fkreek0mvml', 'Access Denied'),
    ('other user', '45f42748-482b-4265-8a8c-73efa872b32b', 'Access Denied')
])
def test_delete_file_project_invalid_team_id(setup, name, team_id, message):
    api = setup['api']
    project_id = setup['default_project']['id']

    res = api.delete_file(team_id=team_id, project_id=project_id, version=0, id="742f0fab-8e9a-4cef-a154-36b2ae08c398")
    assert res.status_code == 203
    assert res.json_response['message'] == message


def test_delete_file_project_valid(setup, new_project):
    api = setup['api']
    project_id = new_project['id']
    team_id = new_project['team_id']

    # check if project has data alredy - try to delete it, if no files in the project - download data first
    res = api.get_list_of_files_for_project(project_id=project_id, team_id=team_id)
    assert res.status_code == 200
    assert res.json_response['message'] == 'success'

    content = res.json_response['data']['content']
    if len(content) == 0:
        # download new data
        sample_file = get_data_file('/authors.csv')

        res = api.get_file_upload_url(project_id=project_id, team_id=team_id, file_name=sample_file)
        assert res.status_code == 200

        res = api.get_list_of_files_for_project(project_id=project_id, team_id=team_id)
        assert res.status_code == 200
        assert res.json_response['message'] == 'success'

        content = res.json_response['data']['content']

    assert len(content) > 0, "Uploaded files have not been found"

    data_id = content[0]['id']
    version = content[0]['version']

    res = api.delete_file(id=data_id, team_id=team_id, project_id=project_id, version=version)
    assert res.status_code == 200
    assert res.json_response['message'] == 'success'

    assert res.json_response['data']['id'] == data_id
    assert res.json_response['data']['projectId'] == project_id
    assert res.json_response['data']['status'] == "DELETED"

    # verify file status
    res = api.get_list_of_files_for_project(project_id=project_id, team_id=team_id)
    assert res.status_code == 200
    assert res.json_response['message'] == 'success'

    content = res.json_response['data']['content']
    assert len(content) > 0, "Uploaded files have not been found"

    uploaded_file = find_dict_in_array_by_value(content, 'id', data_id)
    assert uploaded_file, f"Uploaded file with id {data_id} has not been found"
    assert uploaded_file['id'] == data_id
    assert uploaded_file['status'] == "DELETED"



#  --------- GET  /file/link  --------------------------
def test_get_file_link_invalid_cookies(setup):
    api = QualityFlowApiProject()
    team_id = setup['team_id']
    project_id = setup['default_project']['id']
    path = 'project'

    res = api.get_file_link(team_id=team_id, project_id=project_id, path=path)
    assert res.status_code == 401
    assert res.json_response['message'] == 'Please login'


@pytest.mark.parametrize('name, team_id, message', [
    ('empty', '', 'Unauthorized'),
    ('not exist', 'fkreek0mvml', 'Access Denied'),
    ('other user', '45f42748-482b-4265-8a8c-73efa872b32b', 'Access Denied')
])
def test_get_file_link_invalid_team_id(setup, name, team_id, message):
    api = setup['api']
    project_id = setup['default_project']['id']
    path = 'project'

    res = api.get_file_link(team_id=team_id, project_id=project_id, path=path)
    assert res.status_code == 203
    assert res.json_response['message'] == message


@pytest.mark.parametrize('name, project_id', [
    ('empty', ''),
    ('not exist', 'fkreek0mvml'),
    ('other user', '45f42748-482b-4265-8a8c-73efa872b32b')
])
def test_get_file_link_invalid_project_id(setup, name, project_id):
    api = setup['api']
    team_id = setup['team_id']
    path = 'project'

    res = api.get_file_link(team_id=team_id, project_id=project_id, path=path)

    assert res.status_code == 203
    assert res.json_response['message'] == 'Unauthorized'


def test_get_file_link_valid_existing_project(setup):
    api = setup['api']
    team_id = setup['team_id']
    project_id = setup['default_project']['id']
    path = 'project'

    res = api.get_file_link(team_id=team_id, project_id=project_id, path=path)
    assert res.status_code == 200
    assert res.json_response['message'] == 'success'
    data = res.json_response.get('data', False)
    assert data
    assert data.get('fileLink', False)
    assert data.get('validUntil', False)


def test_get_file_link_valid_new_project(setup, new_project):
    api = setup['api']
    team_id = setup['team_id']
    project_id = new_project['id']
    path = 'project'

    res = api.get_file_link(team_id=team_id, project_id=project_id, path=path)
    assert res.status_code == 200
    assert res.json_response['message'] == 'success'
    data = res.json_response.get('data', False)
    assert data
    assert data.get('fileLink', False)
    assert data.get('validUntil', False)

