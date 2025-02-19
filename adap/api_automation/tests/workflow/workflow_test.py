import logging
import os
import time
import random
from datetime import date

import allure
import pandas as pd
import pytest
import zipfile

from adap.api_automation.services_config.builder import Builder
from adap.api_automation.services_config.workflow import Workflow
from adap.api_automation.services_config.mlapi import MLAPI
from adap.api_automation.utils.data_util import (
    get_user_api_key,
    get_user_team_id,
    get_akon_id,
    get_data_file,
    unzip_file,
    file_exists,
    get_predefined_source_report_wf
)

LOGGER = logging.getLogger(__name__)

pytestmark = [pytest.mark.regression_wf, pytest.mark.adap_api_uat,  pytest.mark.adap_wf_api]

api_key = get_user_api_key('test_account')
team_id = get_user_team_id('test_account')
akon_id = get_akon_id('test_account')
wf_data = pytest.data.predefined_data
PRETRAINED_WATSON_MODEL_FOOTWEAR_ID = wf_data["pretrained_model"][pytest.env]

try:
    predefined_wf = wf_data["workflow_with_judgments"][pytest.env]
except:
    predefined_wf = ''


@pytest.fixture(scope="module")
def general_wf(request):
    wf = Workflow(api_key)
    payload = {'name': 'New WF', 'description': 'API create new wf'}

    res = wf.create_wf(payload=payload)
    print(res.json_response)
    return wf.wf_id


@pytest.fixture(scope="function")
def new_wf(request):
    wf = Workflow(api_key)
    payload = {'name': 'New WF', 'description': 'API create new wf'}
    wf.create_wf(payload=payload)
    return wf.wf_id


def create_jobs(num=2):
    job = Builder(api_key, api_version='v1')
    _jobs = []
    for i in range(num):
        job.create_job()
        _jobs.append(job.job_id)

        # delete jobs after test session
        if os.environ.get("PYTEST_CURRENT_TEST"):
                pytest.data.job_collections[job.job_id] = api_key

    return _jobs


def create_model(num=1):
    model = MLAPI(akon_id, team_id=team_id)
    _models = []
    for i in range(num):
        model.create_model(model_type='ibm-watson-explicit-image-detection')
        _models.append(model.model_id)
    return _models


def get_script():
    wf = Workflow(api_key)
    scripts_catalog = wf.get_scripts_catalog()
    script_idx = random.randint(0, len(scripts_catalog) - 1)
    return scripts_catalog['base_scripts'][script_idx]['latest_version']['base_script_version_id']


# -------------------------------------------------------
# -------------------------------------------------------
# -----------------------------------------------------
#                 TESTS
# -------------------------------------------------------
# -------------------------------------------------------
# -------------------------------------------------------


# TODO: Enable negative cases once https://appen.atlassian.net/browse/CW-8175 is addressed
@allure.parent_suite('/v2/workflows:post')
@pytest.mark.onendone
@pytest.mark.workflow
@pytest.mark.workflow_service
@pytest.mark.workflow_deploy
@pytest.mark.smoke
@pytest.mark.prod_smoke_api
@pytest.mark.adap_api_smoke
@pytest.mark.devspace
@pytest.mark.parametrize('api_key_type, api_key, expected_status',
                         [("valid_key", get_user_api_key('test_account'), 201),
                          ("empty_key", "", 401),
                          ("invalid_key", "12345678qwerty", 401)
                          ])
def test_create_wf(api_key_type, api_key, expected_status):
    wf = Workflow(api_key)
    payload = {'name': 'New WF, date - {}'.format(date.today()), 'description': 'API create new wf'}

    res = wf.create_wf(payload=payload)
    res.assert_response_status(expected_status)


@allure.parent_suite('/v2/workflows:post')
@pytest.mark.workflow
@pytest.mark.workflow_service
def test_create_wf_no_name():
    wf = Workflow(api_key)
    payload = {'name': '', 'description': 'API create new wf'}

    res = wf.create_wf(payload=payload)
    res.assert_response_status(422)


@allure.parent_suite('/v2/workflows/{id}:get')
@pytest.mark.workflow
@pytest.mark.workflow_service
@pytest.mark.workflow_deploy
@pytest.mark.parametrize('api_key_type, api_key, expected_status',
                         [("valid_key", api_key, 200),
                          ("empty_key", "", 401),
                          ("invalid_key", "12345678qwerty", 401)])
def test_read_wf_info(general_wf, api_key_type, api_key, expected_status):
    wf = Workflow(api_key)
    res = wf.get_info(general_wf)
    res.assert_response_status(expected_status)


@allure.parent_suite('/v2/workflows/{id}:get')
@pytest.mark.workflow
# @allure.issue('https://crowdflower.atlassian.net/browse/CP-1990', 'Bug')
def test_user_able_get_info_for_his_job(general_wf):
    _api_key = get_user_api_key('test_predefined_jobs')
    wf = Workflow(_api_key)
    res = wf.get_info(general_wf)
    res.assert_response_status(403)


@allure.parent_suite('/v2/workflows/{id}/compact:get')
@pytest.mark.workflow
@pytest.mark.parametrize('api_key_type, api_key, expected_status',
                         [("valid_key", get_user_api_key('test_account'), 200),
                          ("empty_key", "", 401),
                          ("invalid_key", "12345678qwerty", 401)])
def test_get_wf_owner(general_wf, api_key_type, api_key, expected_status):
    wf = Workflow(api_key)
    res = wf.get_owner(general_wf)
    res.assert_response_status(expected_status)
    if res.status_code == 200:
        assert team_id == res.json_response['team_id']
        assert 'user_id' not in res.json_response


@allure.parent_suite('/v2/workflows/{id}:patch')
@pytest.mark.workflow
@pytest.mark.workflow_deploy
@pytest.mark.workflow_service
@pytest.mark.parametrize('api_key_type, api_key, expected_status',
                         [("valid_key", get_user_api_key('test_account'), 200),
                          ("empty_key", "", 401),
                          ("invalid_key", "12345678qwerty", 401)])
def test_update_wf(general_wf, api_key_type, api_key, expected_status):
    wf = Workflow(api_key)
    payload = {'name': 'My updated workflow', 'description': 'A new description of the workflow'}
    res = wf.update_wf(general_wf, payload)
    res.assert_response_status(expected_status)
    if res.status_code == 200:
        assert res.json_response['name'] == 'My updated workflow'
        assert res.json_response['description'] == 'A new description of the workflow'
        assert res.json_response['id'] == general_wf


@allure.parent_suite('/v2/workflows/{id}:delete')
@pytest.mark.workflow
# @pytest.mark.bug
def test_user_can_only_delete_wf_that_they_own(new_wf):
    """
    This tests ensures that user can only delete their own WFs
    """
    _api_key = get_user_api_key('test_predefined_jobs')
    wf = Workflow(_api_key)
    res = wf.delete_wf(new_wf)
    res.assert_response_status(403)
    print(res.status_code)
    print(res.json_response)


@allure.parent_suite('/v2/workflows/{id}/copy:post')
@pytest.mark.workflow
@pytest.mark.workflow_deploy
@pytest.mark.parametrize('api_key_type, user, expected_status',
                         [("owner_key", 'test_account', 201),
                          ("admin_key", "cf_internal_role", 201),
                          ("non_admin", "standard_user", 404)])
def test_copy_wf(new_wf, api_key_type, user, expected_status):
    _api_key = get_user_api_key(user)
    _wf = Workflow(_api_key)
    res = _wf.copy_wf(new_wf)
    res.assert_response_status(expected_status)

    if res.status_code == 201:
        _copied_wf_id = res.json_response.get('id')
        assert _copied_wf_id is not None, "workflow id was not generated"


@allure.parent_suite('/v2/workflows/{id}/copy:post')
@pytest.mark.workflow
@pytest.mark.smoke
@pytest.mark.prod_smoke_api
@pytest.mark.workflow_deploy
@pytest.mark.adap_api_smoke
def test_copy_wf_jobs():
    _wf = Workflow(api_key)
    _builder = Builder(api_key)

    res = _wf.copy_wf(predefined_wf)
    res.assert_response_status(201)
    _copied_wf_id = res.json_response.get('id')

    _jobs = _wf.get_job_id_from_wf(wf_id=_copied_wf_id)
    for job in _jobs:
        _b_res = _builder.get_json_job_status(job_id=job)
        assert _b_res.json_response.get('workflow_id') == _copied_wf_id, "workflow id does not match!"

        # delete jobs after test session
        if os.environ.get("PYTEST_CURRENT_TEST"):
            pytest.data.job_collections[job] = api_key


@allure.parent_suite('/v2/workflows/{id}/copy:post')
@pytest.mark.skipif("devspace" in pytest.env, reason="broken in adkw0406, no models")
@pytest.mark.workflow
@pytest.mark.smoke
@pytest.mark.adap_api_smoke
@pytest.mark.workflow_deploy
def test_copy_wf_models(new_wf):
    _wf = Workflow(api_key)

    # create a wf with a model step
    models = [PRETRAINED_WATSON_MODEL_FOOTWEAR_ID]
    res = _wf.create_model_step(models, wf_id=new_wf)
    assert len(res) == len(models)

    for step in res:
        assert step['step_id']
        assert step['data_processor_id']
        response = _wf.read_step(step['step_id'], new_wf)

        assert response.json_response['id'] == step['step_id']
        assert response.json_response['data_processor_id'] == step['data_processor_id']

    res = _wf.get_statistics(wf_id=new_wf)
    res.assert_response_status(200)

    # copy the wf with model step
    res = _wf.copy_wf(new_wf)
    res.assert_response_status(201)

    if res.status_code == 201:
        _copied_wf_id = res.json_response.get('id')
        assert _copied_wf_id is not None, "workflow id was not generated"


@allure.parent_suite('/v2/workflows/{id}:delete')
@pytest.mark.workflow
@pytest.mark.smoke
@pytest.mark.prod_smoke_api
@pytest.mark.adap_api_smoke
@pytest.mark.workflow_deploy
@pytest.mark.devspace
def test_delete_new_wf(new_wf):
    wf = Workflow(api_key)
    res = wf.delete_wf(new_wf)
    res.assert_response_status(200)


@allure.parent_suite('/v2/workflows/{id}:delete')
@pytest.mark.workflow
def test_delete_launched_wf():
    wf = Workflow(api_key)
    res = wf.delete_wf(predefined_wf)
    res.assert_response_status(403)
    assert res.json_response['errors'] == "Workflows cannot be deleted once they have been launched"


@allure.parent_suite('/v2/workflows:get')
@pytest.mark.workflow
@pytest.mark.smoke
@pytest.mark.prod_smoke_api
@pytest.mark.workflow_deploy
@pytest.mark.adap_api_smoke
@pytest.mark.devspace
def test_get_list_of_wfs():
    wf = Workflow(api_key)
    res = wf.get_list_of_wfs()
    res.assert_response_status(200)
    for wf in res.json_response['workflows']:
        assert 'user_id' not in wf


@allure.parent_suite('/v2/workflows/counts:get')
@pytest.mark.workflow
@pytest.mark.smoke
@pytest.mark.adap_api_smoke
@pytest.mark.devspace
def test_count_wfs():
    wf = Workflow(api_key)
    res = wf.count_wfs_for_user()
    res.assert_response_status(200)
    # todo assertion  - teams wfs
    print(res.json_response)
    for user in res.json_response['users']:
        assert 'id' not in user


@allure.parent_suite('/v2/workflows/{id}/upload:post')
@allure.issue("https://appen.atlassian.net/browse/DO-11055", "BUG DO-11055")
@pytest.mark.workflow
@pytest.mark.workflow_deploy
@pytest.mark.smoke
@pytest.mark.prod_smoke_api
@pytest.mark.wip
@pytest.mark.adap_api_smoke
@pytest.mark.devspace
@pytest.mark.parametrize('file_type, file',
                         [("csv", "dod_data.csv"),
                          ("ods", "authors.ods"),
                          ("xls", "authors.xls"),
                          ("xlsx", "authors.xlsx"),
                          ("array_on_top_level_json", "animal_urls.json"),
                          ("key_value_obj_json", "animal_urls.jsonl"),
                          ("nested_logic_json", "nested_logic.json"),
                          ("nested_logic_jsonl", "nested_logic.jsonl"),
                          ("tsv", "authors.tsv"),
                          ("file_with_symbols", "special_symbols_file.csv")])
def test_upload_data_valid_files(new_wf, file_type, file):
    sample_file = get_data_file("/" + file)
    wf = Workflow(api_key)
    res = wf.upload_data(sample_file, wf_id=new_wf)
    res.assert_response_status(201)
    data_upload_id = res.json_response['id']
    storage_key = res.json_response['storage_key']
    status = None
    max_try = 90
    current_try = 0
    while status != 'completed' and status != 'failed' and current_try < max_try:
        res = wf.get_data_upload_info(data_upload_id, sample_file, new_wf)
        try:
            status = res.json_response['state']
        except:
            status = None
        time.sleep(1)
        current_try += 1

    assert status == 'completed'

    res = wf.get_list_of_data(sample_file, new_wf)
    res.assert_response_status(200)
    assert res.json_response[0]['id'] == data_upload_id
    assert res.json_response[0]['storage_key'] == storage_key
    assert res.json_response[0]['original_filename'] == file


@allure.parent_suite('/v2/workflows/{id}/upload:post')
@pytest.mark.workflow
@pytest.mark.smoke
@pytest.mark.adap_api_smoke
@pytest.mark.devspace
# @pytest.mark.skip(reason="Depends on https://appen.atlassian.net/browse/CW-7607")
@pytest.mark.parametrize('file_type, file',
                         [("250K", "large_file_numbers_250K.csv"),
                          ("96K", "Appen_Tagging_100_200k_6_17_2021.csv")
                          ])
def test_upload_large_data_file(new_wf, file_type, file):
    sample_file = get_data_file("/large_files/" + file)
    wf = Workflow(api_key)
    res = wf.upload_data(sample_file, wf_id=new_wf, large_file=True)
    assert res.status_code == 201
    data_json = res.json()
    data_upload_id = data_json['id']
    storage_key = data_json['storage_key']
    time.sleep(60)

    status = None
    max_try = 60
    current_try = 0
    while status != 'completed' and status != 'failed' and current_try < max_try:
        res = wf.get_data_upload_info(data_upload_id, sample_file, new_wf)
        status = res.json_response['state']
        time.sleep(1)
        current_try += 1
    assert status == 'completed'

    res = wf.get_list_of_data(sample_file, new_wf)
    res.assert_response_status(200)
    assert res.json_response[0]['id'] == data_upload_id
    assert res.json_response[0]['storage_key'] == storage_key
    assert res.json_response[0]['original_filename'] == file


@allure.parent_suite('/v2/workflows/{id}/upload:post')
@allure.issue("https://appen.atlassian.net/browse/CW-6769", "BUG CW-6769")
@pytest.mark.workflow
@pytest.mark.uat_api
@pytest.mark.parametrize('file_type, file, message',
                         [
                             ("array in lines", "array_in_lines.jsonl",
                              '''Unable to convert to CSV: undefined method `keys' for [{"image_url"=>"http://image1.jpg"}, {"label"=>"cat"}]:Array'''),
                             ("no array", "no_array_at_top_level.json",
                              "Unable to convert to CSV: JSON file is not an array at the top level"),
                             ("invalid elements in json", "invalid_elements_in_json.json",
                              "Unable to convert to CSV"),
                             ("blank headers", "upload_data_files/blank_headers.csv",
                              "One of the uploaded headers was blank. This can happen when a row contains more columns than defined in your header row or one of your headers contains no permitted characters (alphanumeric)."),
                             ("duplicate headers", "upload_data_files/dup_headers.csv",
                              "The uploaded file contains duplicate headers: possible_brands. Please ensure your data file has unique column header names and try again.")
                         ])
def test_upload_data_bad_files(new_wf, file_type, file, message):
    sample_file = get_data_file("/" + file)
    wf = Workflow(api_key)
    res = wf.upload_data(sample_file, wf_id=new_wf)
    res.assert_response_status(201)
    data_upload_id = res.json_response['id']

    res_upload = wf.get_data_upload_info(data_upload_id, sample_file, new_wf)
    res_upload.assert_response_status(200)

    status = None
    max_try = 40
    current_try = 0
    while status != 'failed' and current_try < max_try:
        res = wf.get_data_upload_info(data_upload_id, sample_file, new_wf)
        status = res.json_response['state']
        time.sleep(1)
        current_try += 1
    assert status == 'failed', "Data upload status is {state}".format(state=status)
    assert res.json_response['validation_outcome'].startswith(message)


@allure.parent_suite('/v2/workflows/%s/data_uploads:get,/v2/workflows/{id}/upload:delete')
# @allure.issue("https://appen.atlassian.net/browse/CW-6769", "BUG CW-6769")
# @allure.issue("https://appen.atlassian.net/browse/DO-11055", "BUG DO-11055")
@allure.issue("https://appen.atlassian.net/browse/ADAP-3147", "BUG ADAP-3147")
@pytest.mark.workflow
@pytest.mark.smoke
@pytest.mark.adap_api_smoke
@pytest.mark.devspace
def test_delete_data_upload(general_wf):
    sample_file = get_data_file("/dod_data.csv")
    wf = Workflow(api_key)
    res = wf.upload_data(sample_file, wf_id=general_wf)
    res.assert_response_status(201)
    data_upload_id = res.json_response['id']
    storage_key = res.json_response['storage_key']

    status = None
    max_try = 40
    current_try = 0
    while status != 'completed' and status != 'failed' and current_try < max_try:
        res = wf.get_data_upload_info(data_upload_id, sample_file, general_wf)
        status = res.json_response['state']
        time.sleep(1)
        current_try += 1
    assert status == 'completed'

    res = wf.get_list_of_data(sample_file, general_wf)
    res.assert_response_status(200)
    assert res.json_response[0]['id'] == data_upload_id
    assert res.json_response[0]['storage_key'] == storage_key
    assert res.json_response[0]['original_filename'] == 'dod_data.csv'

    res = wf.delete_data_upload(data_upload_id, general_wf)
    res.assert_response_status(200)
    assert res.json_response == {'message': 'Data successfully deleted.'}


@allure.parent_suite('/v2/workflows/%s/data_uploads:get,/v2/workflows/{id}/upload:delete')
@allure.issue("https://appen.atlassian.net/browse/CW-6769", "BUG CW-6769")
@pytest.mark.workflow
def test_delete_data_upload_invalid_key(general_wf):
    sample_file = get_data_file("/dod_data.csv")
    wf = Workflow(api_key)
    res = wf.upload_data(sample_file, wf_id=general_wf)
    res.assert_response_status(201)
    data_upload_id = res.json_response['id']
    storage_key = res.json_response['storage_key']

    status = None
    max_try = 40
    current_try = 0
    while status != 'completed' and status != 'failed' and current_try < max_try:
        res = wf.get_data_upload_info(data_upload_id, sample_file, general_wf)
        status = res.json_response['state']
        time.sleep(1)
        current_try += 1
    assert status == 'completed'

    res = wf.get_list_of_data(sample_file, general_wf)
    res.assert_response_status(200)
    assert res.json_response[0]['id'] == data_upload_id
    assert res.json_response[0]['storage_key'] == storage_key
    assert res.json_response[0]['original_filename'] == 'dod_data.csv'

    _wf = Workflow("invalid_key")
    res = _wf.delete_data_upload(data_upload_id, general_wf)
    res.assert_response_status(401)


# @pytest.mark.workflow
# @allure.issue('https://crowdflower.atlassian.net/browse/CW-4665', 'Bug CW-4665')
# @pytest.mark.skip
# def test_add_untrained_model_step(new_wf):
#     models = create_model()
#     wf = Workflow(api_key)
#
#     res = wf.create_job_step(models, new_wf)
#     assert len(res) == len(models)
#
#     for step in res:
#         assert step['step_id'] is not None
#         assert step['data_processor_id'] is not None
#         response = wf.read_step(step['step_id'], new_wf)
#
#         assert response.json_response['id'] == step['step_id']
#         assert response.json_response['data_processor_id'] == step['data_processor_id']
#
#     res = wf.get_statistics(wf_id=new_wf)
#     res.assert_response_status(403)


@allure.parent_suite('/v2/workflows/{id}/steps:post,/v2/workflows/{id}/statistics:get')
@pytest.mark.workflow
@pytest.mark.smoke
@pytest.mark.prod_smoke_api
@pytest.mark.adap_api_smoke
@pytest.mark.devspace
def test_create_step(new_wf):
    jobs = create_jobs()
    wf = Workflow(api_key)

    res = wf.create_job_step(jobs, new_wf)
    assert len(res) == len(jobs)

    for step in res:
        assert step['step_id'] is not None
        assert step['data_processor_id'] is not None
        #   read steps
        response = wf.read_step(step['step_id'], new_wf)

        assert response.json_response['id'] == step['step_id']
        assert response.json_response['data_processor_id'] == step['data_processor_id']

    res = wf.get_statistics(wf_id=new_wf)
    res.assert_response_status(200)
    # todo assert payload


@allure.parent_suite('/v2/workflows/{id}/steps:delete')
@pytest.mark.workflow
@pytest.mark.smoke
@pytest.mark.prod_smoke_api
@pytest.mark.adap_api_smoke
@pytest.mark.devspace
def test_delete_step(new_wf):
    wf = Workflow(api_key)
    jobs = create_jobs()

    new_steps = wf.create_job_step(jobs, new_wf)
    assert len(new_steps) == len(jobs)

    res = wf.delete_step(new_steps[0]['step_id'], new_wf)
    res.assert_response_status(204)

    all_steps = wf.list_of_steps(new_wf)
    all_steps.assert_response_status(200)
    assert len(all_steps.json_response) == len(new_steps) - 1
    assert all_steps.json_response[0]['id'] == new_steps[1]['step_id']


@allure.parent_suite('/v2/workflows/{id}/steps/{step_id}/routes:post')
@pytest.mark.workflow
@pytest.mark.smoke
@pytest.mark.prod_smoke_api
@pytest.mark.workflow_deploy
@pytest.mark.workflow_engine_deploy
@pytest.mark.adap_api_smoke
@pytest.mark.devspace
def test_create_route(new_wf):
    wf = Workflow(api_key)
    jobs = create_jobs()

    new_steps = wf.create_job_step(jobs, new_wf)
    assert len(new_steps) >= 2

    step_id = new_steps[0]['step_id']
    destination_step_id = new_steps[1]['step_id']

    res = wf.create_route(step_id, destination_step_id, new_wf)

    res.assert_response_status(201)
    assert res.json_response['workflow_step_id'] == step_id
    assert res.json_response['destination_step_id'] == destination_step_id

    route_id = res.json_response['id']
    res = wf.read_route(step_id, route_id, new_wf)
    res.assert_response_status(200)
    assert res.json_response['workflow_step_id'] == step_id
    assert res.json_response['destination_step_id'] == destination_step_id


@allure.parent_suite('/v2/workflows/{id}/steps/{step_id}/routes/{route_id}:patch')
@pytest.mark.workflow
@pytest.mark.workflow_engine_deploy
def test_update_route(new_wf):
    jobs = create_jobs(3)
    wf = Workflow(api_key)

    new_steps = wf.create_job_step(jobs, new_wf)
    assert len(new_steps) == 3

    step_id = new_steps[0]['step_id']
    destination_step_id = new_steps[1]['step_id']
    update_destination_step_id = new_steps[2]['step_id']

    res = wf.create_route(step_id, destination_step_id, new_wf)
    route_id = res.json_response['id']
    assert res.json_response['workflow_step_id'] == step_id
    assert res.json_response['destination_step_id'] == destination_step_id

    res = wf.update_route(step_id, route_id, update_destination_step_id, new_wf)
    assert res.json_response['workflow_step_id'] == step_id
    assert res.json_response['destination_step_id'] == update_destination_step_id

    res = wf.read_route(step_id, route_id, new_wf)
    assert res.json_response['workflow_step_id'] == step_id
    assert res.json_response['destination_step_id'] == update_destination_step_id


@allure.parent_suite('/v2/workflows/{}id/steps/{step_id}/routes/{route_id}:delete')
@pytest.mark.workflow
@pytest.mark.workflow_engine_deploy
def test_delete_route(new_wf):
    jobs = create_jobs()
    wf = Workflow(api_key)

    new_steps = wf.create_job_step(jobs, new_wf)

    step_id = new_steps[0]['step_id']
    destination_step_id = new_steps[1]['step_id']

    route_id = wf.create_route(step_id, destination_step_id, new_wf).json_response['id']

    res = wf.delete_route(step_id, route_id, new_wf)
    res.assert_response_status(204)

    res = wf.read_route(step_id, route_id, new_wf)
    assert res.json_response == {'message': 'The resource you requested was not found'}


@allure.parent_suite('/v2/workflows/{}id/steps/{step_id}/routes/{route_id}:delete')
@pytest.mark.workflow
def test_delete_invalid_route(new_wf):
    jobs = create_jobs()
    wf = Workflow(api_key)

    new_steps = wf.create_job_step(jobs, new_wf)

    step_id = new_steps[0]['step_id']
    destination_step_id = new_steps[1]['step_id']

    route_id = wf.create_route(step_id, destination_step_id, new_wf).json_response['id']

    res = wf.delete_route(step_id, route_id + 1, new_wf)
    res.assert_response_status(404)
    assert res.json_response == {'message': 'The resource you requested was not found'}


@allure.parent_suite('/v2/workflows/{}id/steps/{step_id}/routes:get')
@pytest.mark.workflow
@pytest.mark.workflow_engine_deploy
def test_list_of_routers(new_wf):
    jobs = create_jobs(3)
    wf = Workflow(api_key)

    new_steps = wf.create_job_step(jobs, new_wf)

    step_id = new_steps[0]['step_id']
    destination1_step_id = new_steps[1]['step_id']
    destination2_step_id = new_steps[2]['step_id']

    #  route1
    wf.create_route(step_id, destination1_step_id, new_wf)
    #  route2
    wf.create_route(step_id, destination2_step_id, new_wf)

    res = wf.get_list_of_routes(step_id, new_wf)
    res.assert_response_status(200)
    assert len(res.json_response) == 2
    assert res.json_response[0]['workflow_step_id'] == step_id
    assert res.json_response[0]['destination_step_id'] == destination2_step_id
    assert res.json_response[1]['workflow_step_id'] == step_id
    assert res.json_response[1]['destination_step_id'] == destination1_step_id


@allure.parent_suite('/v2/workflows/{id}/steps/{step_id}/routes/{route_id}/rules:post')
@pytest.mark.workflow
@pytest.mark.smoke
@pytest.mark.prod_smoke_api
@pytest.mark.adap_api_smoke
@pytest.mark.workflow_engine_deploy
@pytest.mark.devspace
def test_create_and_filter_rule(new_wf):
    jobs = create_jobs(2)
    wf = Workflow(api_key)

    new_steps = wf.create_job_step(jobs, new_wf)

    step_id = new_steps[0]['step_id']
    destination1_step_id = new_steps[1]['step_id']

    #  route
    route_id = wf.create_route(step_id, destination1_step_id, new_wf).json_response['id']

    payload = {
        "filter_rule": {
            "comparison_field": "label",
            "comparison_operation": "!=",
            "comparison_value": "cat",
            "rule_connector": "and"
        }
    }
    res = wf.create_filter_rule(step_id, route_id, payload, new_wf)
    res.assert_response_status(201)

    assert res.json_response['comparison_field'] == 'label'
    assert res.json_response['comparison_operation'] == '!='
    assert res.json_response['comparison_value'] == 'cat'
    assert res.json_response['rule_connector'] == 'and'

    rule_id = res.json_response['id']

    res = wf.read_filter_rule(step_id, route_id, rule_id, new_wf)
    res.assert_response_status(200)
    assert res.json_response['id'] == rule_id


@allure.parent_suite('/v2/workflows/{id}/steps/{step_id}/routes/{route_id}/rules:post')
@pytest.mark.workflow
def test_create_rnd_filter_rule(new_wf):
    jobs = create_jobs(2)
    wf = Workflow(api_key)

    new_steps = wf.create_job_step(jobs, new_wf)

    step_id = new_steps[0]['step_id']
    destination1_step_id = new_steps[1]['step_id']

    #  route
    route_id = wf.create_route(step_id, destination1_step_id, new_wf).json_response['id']

    _rnd = random.randint(1, 100)
    payload = {
        "filter_rule": {
            "comparison_value": _rnd,
            "rule_connector": "rnd"
        }
    }
    res = wf.create_filter_rule(step_id, route_id, payload, new_wf)
    res.assert_response_status(201)

    assert not res.json_response['comparison_field']
    assert not res.json_response['comparison_operation']
    assert res.json_response['comparison_value'] == _rnd.__str__()
    assert res.json_response['rule_connector'] == 'rnd'

    rule_id = res.json_response['id']

    res = wf.read_filter_rule(step_id, route_id, rule_id, new_wf)
    res.assert_response_status(200)
    assert res.json_response['id'] == rule_id


@allure.parent_suite('/v2/workflows/{id}/steps/{step_id}/routes/{route_id}/rules:post')
@pytest.mark.workflow
@pytest.mark.workflow_engine_deploy
@pytest.mark.parametrize('value, message',
                         [(0, "Comparison value must be greater than or equal to 1"),
                          (-1, "Comparison value must be greater than or equal to 1"),
                          (100, "Comparison value must be less than or equal to 99"),
                          ("text", "Comparison value is not a number")])
def test_create_rnd_filter_rule_validation(new_wf, value, message):
    jobs = create_jobs(2)
    wf = Workflow(api_key)

    new_steps = wf.create_job_step(jobs, new_wf)

    step_id = new_steps[0]['step_id']
    destination1_step_id = new_steps[1]['step_id']

    route_id = wf.create_route(step_id, destination1_step_id, new_wf).json_response['id']

    payload = {
        "filter_rule": {
            "comparison_value": value,
            "rule_connector": "rnd"
        }
    }
    res = wf.create_filter_rule(step_id, route_id, payload, new_wf)
    res.assert_response_status(422)
    assert res.json_response['errors'] == [message]


@allure.parent_suite('/v2/workflows/{id}/steps/{step_id}/routes/{route_id}/rules:post')
@pytest.mark.workflow
@pytest.mark.workflow_engine_deploy
def test_create_els_filter_rule(new_wf):
    jobs = create_jobs(3)
    wf = Workflow(api_key)
    step1, step2, step3 = (step['step_id'] for step in wf.create_job_step(jobs, new_wf))

    route_1_2 = wf.create_route(step1, step2, new_wf).json_response['id']
    route_1_3 = wf.create_route(step1, step3, new_wf).json_response['id']

    rnd_rule_resp = wf.create_filter_rule(
        step1,
        route_1_2,
        {
            "filter_rule": {
                "comparison_value": 10,
                "rule_connector": "rnd"
            }
        },
        new_wf)

    els_rule_resp = wf.create_filter_rule(
        step1,
        route_1_3,
        {
            "filter_rule": {
                "rule_connector": "els"
            }
        },
        new_wf)

    assert els_rule_resp.json_response['comparison_field'] is None
    assert els_rule_resp.json_response['comparison_operation'] is None
    assert els_rule_resp.json_response['comparison_value'] is None
    assert els_rule_resp.json_response['rule_connector'] == 'els'

    rule_id = els_rule_resp.json_response['id']

    res = wf.read_filter_rule(step1, route_1_3, rule_id, new_wf)
    res.assert_response_status(200)
    assert res.json_response['id'] == rule_id


@allure.parent_suite('/v2/workflows/{id}/steps/{step_id}/routes/{route_id}/rules:post')
@pytest.mark.workflow
@pytest.mark.workflow_engine_deploy
@pytest.mark.parametrize('value, message',
                         [(0, "Comparison value must be greater than or equal to 1"),
                          (-1, "Comparison value must be greater than or equal to 1"),
                          (100, "Comparison value must be less than or equal to 99"),
                          ("text", "Comparison value is not a number")])
def test_create_csp_filter_rule_validation(new_wf, value, message):
    jobs = create_jobs(2)
    wf = Workflow(api_key)

    new_steps = wf.create_job_step(jobs, new_wf)

    step_id = new_steps[0]['step_id']
    destination1_step_id = new_steps[1]['step_id']

    route_id = wf.create_route(step_id, destination1_step_id, new_wf).json_response['id']

    payload = {
        "filter_rule": {
            "comparison_value": value,
            "rule_connector": "csp"
        }
    }
    res = wf.create_filter_rule(step_id, route_id, payload, new_wf)
    res.assert_response_status(422)
    assert res.json_response['errors'] == [message]


@allure.parent_suite('/v2/workflows/{id}/steps/{step_id}/routes/{route_id}/rules:post')
@pytest.mark.workflow
@pytest.mark.workflow_engine_deploy
def test_create_invalid_filter_rule(new_wf):
    jobs = create_jobs(2)
    wf = Workflow(api_key)

    new_steps = wf.create_job_step(jobs, new_wf)

    step_id = new_steps[0]['step_id']
    destination1_step_id = new_steps[1]['step_id']

    #  route
    route_id = wf.create_route(step_id, destination1_step_id, new_wf).json_response['id']

    payload = {
        "filter_rule": {
            "comparison_value": "20",
            "rule_connector": "rand"
        }
    }
    res = wf.create_filter_rule(step_id, route_id, payload, new_wf)
    res.assert_response_status(422)
    print(res.json_response['errors'])
    assert res.json_response['errors'] == [
        "Rule connector 'rand' must be one of [\"all\", \"els\", \"and\", \"or\", \"rnd\", \"csp\"]"]


# TODO: Add more verification checks
@allure.parent_suite('/v2/workflows/{id}/steps/{step_id}/routes/{route_id}/rules:post')
@pytest.mark.workflow
@pytest.mark.workflow_engine_deploy
def test_create_or_filter_rule(new_wf):
    jobs = create_jobs(2)
    wf = Workflow(api_key)
    rule_id = []

    new_steps = wf.create_job_step(jobs, new_wf)

    step_id = new_steps[0]['step_id']
    destination1_step_id = new_steps[1]['step_id']

    route_id = wf.create_route(step_id, destination1_step_id, new_wf).json_response['id']

    payload = {
        "filter_rule":
            {
                "comparison_field": "label",
                "comparison_operation": "==",
                "comparison_value": "cat",
                "rule_connector": "or"
            }
    }

    payload_2 = {
        "filter_rule":
            {
                "comparison_field": "label",
                "comparison_operation": "==",
                "comparison_value": "dog",
                "rule_connector": "or"
            }
    }
    res = wf.create_filter_rule(step_id, route_id, payload, new_wf)
    res.assert_response_status(201)
    rule_id.append(res.json_response['id'])

    res_1 = wf.create_filter_rule(step_id, route_id, payload_2, new_wf)
    res_1.assert_response_status(201)
    rule_id.append(res_1.json_response['id'])

    res_list = wf.list_filter_rule(step_id, route_id, new_wf)
    res_list.assert_response_status(200)
    assert len(res_list.json_response) == 2


@allure.parent_suite('/v2/workflows/{id}/steps/{step_id}/routes/{route_id}/rules:post')
@pytest.mark.workflow
@pytest.mark.workflow_engine_deploy
def test_create_csp_filter_rule(new_wf):
    jobs = create_jobs(2)
    wf = Workflow(api_key)

    new_steps = wf.create_job_step(jobs, new_wf)

    step_id = new_steps[0]['step_id']
    destination1_step_id = new_steps[1]['step_id']

    route_id = wf.create_route(step_id, destination1_step_id, new_wf).json_response['id']

    _cv = random.randint(1, 100)
    payload = {
        "filter_rule": {
            "comparison_value": _cv,
            "rule_connector": "csp"
        }
    }
    res = wf.create_filter_rule(step_id, route_id, payload, new_wf)
    res.assert_response_status(201)

    assert not res.json_response['comparison_field']
    assert not res.json_response['comparison_operation']
    assert res.json_response['comparison_value'] == _cv.__str__()
    assert res.json_response['rule_connector'] == 'csp'

    rule_id = res.json_response['id']

    res = wf.read_filter_rule(step_id, route_id, rule_id, new_wf)
    res.assert_response_status(200)
    assert res.json_response['id'] == rule_id


@allure.parent_suite('/v2/workflows/{id}/steps/{step_id}/routes/{route_id}/rules:post')
@pytest.mark.workflow
@pytest.mark.workflow_engine_deploy
def test_create_all_filter_rule(new_wf):
    jobs = create_jobs(2)
    wf = Workflow(api_key)

    new_steps = wf.create_job_step(jobs, new_wf)

    step_id = new_steps[0]['step_id']
    destination1_step_id = new_steps[1]['step_id']

    route_id = wf.create_route(step_id, destination1_step_id, new_wf).json_response['id']

    payload = {
        "filter_rule": {
            "rule_connector": "all"
        }
    }
    res = wf.create_filter_rule(step_id, route_id, payload, new_wf)
    res.assert_response_status(201)

    assert not res.json_response['comparison_field']
    assert not res.json_response['comparison_operation']
    assert not res.json_response['comparison_value']
    assert res.json_response['rule_connector'] == 'all'

    rule_id = res.json_response['id']

    res = wf.read_filter_rule(step_id, route_id, rule_id, new_wf)
    res.assert_response_status(200)
    assert res.json_response['id'] == rule_id


@allure.parent_suite(
    '/v2/workflows/{id}/steps/{step_id}/routes/{route_id}/rules/{filter_id}:patch,/v2/workflows/{id}/steps/{'
    'step_id}/routes/{route_id}/rules/{filter_id}:delete')
@pytest.mark.workflow
@pytest.mark.workflow_engine_deploy
def test_update_delete_filter_rule(new_wf):
    jobs = create_jobs(2)
    wf = Workflow(api_key)

    new_steps = wf.create_job_step(jobs, new_wf)

    step_id = new_steps[0]['step_id']
    destination1_step_id = new_steps[1]['step_id']

    #  route
    route_id = wf.create_route(step_id, destination1_step_id, new_wf).json_response['id']

    payload = {
        "filter_rule": {
            "comparison_field": "label",
            "comparison_operation": "!=",
            "comparison_value": "cat",
            "rule_connector": "and"
        }
    }
    res = wf.create_filter_rule(step_id, route_id, payload, new_wf)
    res.assert_response_status(201)
    rule_id = res.json_response['id']

    payload = {
        "filter_rule": {
            "comparison_field": "label",
            "comparison_operation": "!=",
            "comparison_value": "dog",
            "rule_connector": "and"
        }
    }
    res = wf.update_filter_rule(step_id, route_id, rule_id, payload, new_wf)
    res.assert_response_status(200)
    assert res.json_response['comparison_field'] == 'label'
    assert res.json_response['comparison_operation'] == '!='
    assert res.json_response['comparison_value'] == 'dog'
    assert res.json_response['rule_connector'] == 'and'

    res = wf.read_filter_rule(step_id, route_id, rule_id, new_wf)
    res.assert_response_status(200)
    assert res.json_response['id'] == rule_id

    res = wf.list_filter_rule(step_id, route_id, new_wf)
    res.assert_response_status(200)
    assert len(res.json_response) == 1
    assert res.json_response[0]['comparison_value'] == 'dog'
    assert res.json_response[0]['comparison_field'] == 'label'
    assert res.json_response[0]['comparison_operation'] == '!='
    assert res.json_response[0]['rule_connector'] == 'and'

    #  delete filter rule
    res = wf.delete_filter_rule(step_id, route_id, rule_id, new_wf)
    res.assert_response_status(204)

    res = wf.list_filter_rule(step_id, route_id, new_wf)
    assert res.json_response == []


@allure.parent_suite('/v2/workflows/{id}/report/regenerate:post')
@pytest.mark.workflow
@pytest.mark.smoke
@pytest.mark.adap_api_smoke
@pytest.mark.workflow_deploy
@pytest.mark.parametrize('report_type', ["source", "full"])
@pytest.mark.devspace
def test_regenerate_report_valid(report_type):
    _wf = Workflow(api_key)

    resp = _wf.regenerate_report(report_type, predefined_wf)
    assert resp.status_code == 201 or 202

    if resp.status_code == 202:
        resp.assert_job_message("{report_type} report for workflow {wf_id} is being generated".format(
            report_type=report_type.capitalize(), wf_id=predefined_wf))
    else:
        resp.assert_job_message("{report_type} report for workflow {wf_id} is ready for download".format(
            report_type=report_type.capitalize(), wf_id=predefined_wf))


@allure.parent_suite('/v2/workflows/{id}/report/regenerate:post')
@pytest.mark.workflow
@pytest.mark.parametrize('scenario, wf_id_input, expected_status',
                         [("nonexistent_wf", "0", 404),
                          ("integer_wf", 0, 400),
                          ("negative_wf_id", -1, 400),
                          ("empty_wf", "", 400),
                          ("test_wf", "12345678qwerty", 400)])
def test_regenerate_report_invalid_wf_id(scenario, wf_id_input, expected_status):
    _wf = Workflow(api_key)

    report_type = 'source'
    resp = _wf.regenerate_report(report_type, wf_id_input)
    resp.assert_response_status(expected_status)


@allure.parent_suite('/v2/workflows/{id}/report/regenerate:post')
@pytest.mark.workflow
@pytest.mark.parametrize('report_type', ["Source", "Full", "random"])
def test_regenerate_report_invalid_report_type(report_type):
    _wf = Workflow(api_key)

    resp = _wf.regenerate_report(report_type, predefined_wf)
    resp.assert_response_status(422)
    resp.assert_error_message_v2("Invalid type={0}".format(report_type))


@allure.parent_suite('/v2/workflows/{id}/report/download:get')
@pytest.mark.workflowy
@pytest.mark.smoke
@pytest.mark.adap_api_smoke
@pytest.mark.workflow_deploy
def test_download_source_report_valid(tmpdir):
    _wf = Workflow(api_key)

    resp = _wf.download_report('source', predefined_wf)
    resp.assert_response_status(200)

    zipname = tmpdir + '/{0}_workflow_source_report.zip'.format(pytest.env)
    open(zipname, 'wb').write(resp.content)
    zf = zipfile.ZipFile(zipname)
    files = zf.infolist()
    # check at least one file
    assert files
    # attempt to parse all source files as CSV
    for source_file in files:
        print(source_file.filename)
        _df = pd.read_csv(zf.open(source_file.filename))
        print(_df.columns)

    LOGGER.info("Cleaning up files")
    os.remove(zipname)


@allure.parent_suite('/v2/workflows/{id}/report/download:get')
@pytest.mark.skipif("devspace" in pytest.env, reason="broken in adkw0406, no athena")
@allure.issue('"https://appen.atlassian.net/browse/ADAP-3149"', 'Bug ADAP-3149')
@pytest.mark.workflow
@pytest.mark.smoke
@pytest.mark.adap_api_smoke
@pytest.mark.workflow_deploy
def test_download_full_report_valid(tmpdir):
    _wf = Workflow(api_key)

    report_type = 'full'
    filename = "/workflow_{0}_report.csv".format(predefined_wf)

    resp = _wf.download_report(report_type, predefined_wf)
    try:
        if resp.status_code == 204:
            assert resp.content['message'] == "Full report for workflow {id} is being generated".format(id=_wf.wf_id), \
                f"Full Report for workflow {id} not generated or message changed"
    except ValueError:
        LOGGER.info("Report is still being generated. Exiting test...")

    resp.assert_response_status(200)
    open(tmpdir + '/{0}.zip'.format(report_type), 'wb').write(resp.content)
    unzip_file(tmpdir + '/{0}.zip'.format(report_type))

    csv_name = tmpdir + filename

    try:
        if file_exists(csv_name):
            LOGGER.info('csv file exists')
    except ValueError:
        LOGGER.info('csv file does not exist')

    _df = pd.read_csv(csv_name)
    LOGGER.info(_df.columns)

    LOGGER.info("Cleaning up files")
    os.remove(csv_name)
    os.remove(tmpdir + '/{0}.zip'.format(report_type))


@allure.parent_suite('/v2/workflows/{id}/report/download:get')
@pytest.mark.workflow
@pytest.mark.parametrize('report_type', ["source", "full"])
def test_download_report_without_regeneration(report_type, general_wf):
    _wf = Workflow(api_key, wf_id=general_wf)

    resp = _wf.download_report(report_type, _wf.wf_id)
    resp.assert_response_status(202)
    resp.assert_job_message('{report_type} report for workflow {id} is being generated'.format(
        report_type=report_type.capitalize(), id=_wf.wf_id))
    assert resp.headers['content-disposition'], "json attachment is not generated"


@allure.parent_suite('/scripts/catalog:get')
@pytest.mark.workflow
def test_get_scripts_catalog():
    _wf = Workflow(api_key)
    res = _wf.get_scripts_catalog()

    for script in res['base_scripts']:
        assert script['script_title']
        assert script['latest_version']['base_script_version_id']
        assert script['latest_version_id']


@pytest.mark.workflow
def test_add_script_step_wf(new_wf):
    wf = Workflow(api_key)
    script_id = get_script()

    res = wf.create_script_step(script_id, wf_id=new_wf)
    for step in res:
        assert step['step_id'] is not None
        assert step['data_processor_id'] is not None
        response = wf.read_step(step['step_id'], new_wf)

        assert response.json_response['id'] == step['step_id']
        assert response.json_response['data_processor_id'] == step['data_processor_id']


@pytest.mark.workflow
@pytest.mark.smoke
def test_copy_script_wf(new_wf):
    wf = Workflow(api_key)
    script_id = get_script()

    wf.create_script_step(script_id, wf_id=new_wf)
    res_copy = wf.copy_wf(new_wf)
    res_copy.assert_response_status(201)

    if res_copy.status_code == 201:
        _copied_wf_id = res_copy.json_response.get('id')
        assert _copied_wf_id is not None, "workflow id was not generated"
