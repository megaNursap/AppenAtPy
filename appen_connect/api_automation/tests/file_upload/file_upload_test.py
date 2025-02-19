import datetime

from adap.api_automation.utils.data_util import *
from appen_connect.api_automation.services_config.file_upload import FileUploadAPI

pytestmark = [pytest.mark.regression_ac_file_upload, pytest.mark.regression_ac, pytest.mark.ac_api_v2, pytest.mark.ac_file_upload]

UPLOAD_TYPE = "PRODUCTIVITY_DATA"
CLIENT_ID = 1

faker = Faker()
random_prefix = faker.zipcode()

NEW_FILE_NAME = "file_upload_{}.xlsx".format(random_prefix)
TEMPLATE_NAME = "template_using_automation_{}".format(random_prefix)


# TODO - ask developer how can we make this metadata available from the partner data column mapping and can be used it for getting Project/USER Mapping and column Headers


def test_get_presigned_url(ac_api_cookie):
    api = FileUploadAPI(ac_api_cookie)
    res = api.get_presigned_url(CLIENT_ID, UPLOAD_TYPE, NEW_FILE_NAME)
    res.assert_response_status(200)
    assert res.json_response['preSignedUrl'] != ''


def test_upload_file(ac_api_cookie, tmpdir):
    sample_file = get_data_file("/File_Upload_sample1.xlsx")
    new_sample = copy_file_with_new_name(sample_file, tmpdir, NEW_FILE_NAME)
    api = FileUploadAPI(ac_api_cookie)
    payload = {
        "filePath": new_sample,
        "clientId": CLIENT_ID,
        "type": UPLOAD_TYPE
    }
    res = api.upload_file(payload=payload)
    res.assert_response_status(200)
    assert len(res.json_response) >0


def test_get_uploaded_file_by_id(ac_api_cookie, tmpdir):
    sample_file = get_data_file("/File_Upload_sample1.xlsx")
    new_sample = copy_file_with_new_name(sample_file, tmpdir, NEW_FILE_NAME)
    api = FileUploadAPI(ac_api_cookie)
    payload = {
        "filePath": new_sample,
        "clientId": CLIENT_ID,
        "type": UPLOAD_TYPE
    }
    res = api.upload_file(payload=payload)
    res.assert_response_status(200)
    file_id = res.json_response['fileId']
    res1 = api.get_uploaded_file_by_id(file_id)
    res1.assert_response_status(200)
    assert "/"+ res1.json_response['name'] == new_sample


def test_get_column_mapping_by_client_id(ac_api_cookie):
    api = FileUploadAPI(ac_api_cookie)
    res = api.get_column_mapping_client_id(CLIENT_ID, type=UPLOAD_TYPE)
    res.assert_response_status(200)
    assert len(res.json_response['mappings']) > 0


def test_check_template_name_exists(ac_api_cookie):
    api = FileUploadAPI(ac_api_cookie)
    res = api.check_template_exists(template_name=TEMPLATE_NAME)
    res.assert_response_status(200)
    assert (res.json_response['name'] == TEMPLATE_NAME)
    assert (res.json_response['exists'] == False)


def test_get_column_headers(ac_api_cookie, tmpdir):
    sample_file = get_data_file("/File_Upload_sample1.xlsx")
    new_sample = copy_file_with_new_name(sample_file, tmpdir, NEW_FILE_NAME)
    api = FileUploadAPI(ac_api_cookie)

    payload = {
        "filePath": new_sample,
        "clientId": CLIENT_ID,
        "type": UPLOAD_TYPE
    }
    res = api.upload_file(payload=payload)
    res.assert_response_status(200)
    file_id = res.json_response['fileId']
    res1 = api.get_column_headers(file_id)
    res1.assert_response_status(500)
    #Error message is not consistent so not asserting that
    assert len(res1.json_response) >0


def test_get_column_types(ac_api_cookie):
    api = FileUploadAPI(ac_api_cookie)
    res = api.get_column_types()
    res.assert_response_status(200)
    assert len(res.json_response['types']) > 0


def test_file_upload_end_to_end(ac_api_cookie, tmpdir):
    api = FileUploadAPI(ac_api_cookie)
    sample_file = get_data_file("/File_Upload_sample1.xlsx")

    # Get pre-signed-url
    res = api.get_presigned_url(CLIENT_ID, UPLOAD_TYPE, NEW_FILE_NAME)
    res.assert_response_status(200)
    assert res.json_response['preSignedUrl'] != ''

    # Upload File
    new_sample = copy_file_with_new_name(sample_file, tmpdir, NEW_FILE_NAME)
    payload = {
        "filePath": new_sample,
        "clientId": CLIENT_ID,
        "type": UPLOAD_TYPE
    }
    res = api.upload_file(payload=payload)
    res.assert_response_status(200)
    file_id = res.json_response['fileId']
    assert res.json_response['fileId'] != 0

    # Column Mapping
    payload = {
        "clientId": 1,
        "type": UPLOAD_TYPE,
        "name": TEMPLATE_NAME,
        "timezone": "US/Pacific",
        "columnsInfo": {
            "userProjectInfo": {
                "containProjectData": True,
                "acProjectIdColumn": "",
                "acProjectIdColumnError": "",
                "projectId": None,
                "externalProjectIdColumns": [
                    "queue"
                ],
                "externalProjectIdColumnsError": "",
                "projectError": None,
                "projectStatus": "EDITED",
                "acUserIdColumn": None,
                "externalUserIdColumns": [
                    "user_id"
                ],
                "externalUserIdColumnsError": "",
                "clientStatus": "COMPLETE"
            },
            "projectAlias": "",
            "projectError": None,
            "userError": None,
            "dateOfWorkInfoDto": {
                "externalDateError": "",
                "dateWorkError": "",
                "dateOfWork": None,
                "externalDateOfWorkColumn": "day",
                "status": "COMPLETE"
            },
            "dateOfWorkError": None,
            "timeWorkedInfo": {
                "columns": [
                    {
                        "key": "e7657037-ab22-4dd3-85f2-a826f6c5c97f",
                        "columnName": "total_review_time",
                        "columnNameError": "",
                        "columnUnit": "MINUTES",
                        "columnUnitError": "",
                        "columnWeight": 1,
                        "columnRounding": 0
                    }
                ],
                "orConditions": [

                ],
                "calculationMethod": "MATH",
                "calculateByCells": True,
                "status": "COMPLETE"
            },
            "containsTimeWorked": True,
            "timeWorkedError": None,
            "unitsCompletedError": None
        }
    }
    res = api.create_column_mapping(payload=payload)
    res.assert_response_status(200)
    column_mapping_id = res.json_response['id']
    # Get Columns
    res1 = api.get_columns(column_mapping_id)
    res1.assert_response_status(200)

    # Update uploaded file with column mapping
    payload = {
        'columnMappingId': column_mapping_id
    }
    res_updated_file = api.update_partner_data_file_with_mapping(file_id, payload=payload)
    res_updated_file.assert_response_status(200)
    assert res_updated_file.json_response['id'] == file_id
    assert res_updated_file.json_response['clientId'] == CLIENT_ID

    # Project Mapping
    res_project_mapping = api.create_project_mapping(file_id)
    res_project_mapping.assert_response_status(500)
    print("PROJECT MAPPING", res_project_mapping.json_response)
    assert res_project_mapping.json_response[
                'message'] == "FILE UPLOAD - Not ready for processing, metadata is not set for file id {}, mapping id {}".format(
        file_id, column_mapping_id)

    # Project Mapped rows
    res_project_mapped_rows = api.get_project_mapped_rows_count(file_id)
    res_project_mapped_rows.assert_response_status(200)
    print("PROJECT MAPPED ROWS", res_project_mapping.json_response)

    # User Mapping
    res_user_mapping = api.create_user_mapping(file_id)
    res_user_mapping.assert_response_status(500)
    print("USER MAPPING", res_user_mapping.json_response)
    assert res_user_mapping.json_response[
                'message'] == "FILE UPLOAD - Not ready for processing, metadata is not set for file id {}, mapping id {}".format(
        file_id, column_mapping_id)


    # User Mapped rows
    res_user_mapped_rows = api.get_project_mapped_rows_count(file_id)
    res_user_mapped_rows.assert_response_status(200)
    assert len(res_user_mapped_rows.json_response) >0


# @pytest.mark.skip(reason="not stable")
# def test_get_project_mapping_download_with_incorrect_file_status(ac_api_cookie, tmpdir):
#     api = FileUploadAPI(ac_api_cookie)
#     sample_file = get_data_file("/File_Upload_sample1.xlsx")
#     new_sample = copy_file_with_new_name(sample_file, tmpdir, NEW_FILE_NAME)
#     payload = {
#         "filePath": new_sample,
#         "clientId": CLIENT_ID,
#         "type": UPLOAD_TYPE
#     }
#     res = api.upload_file(payload=payload)
#     res.assert_response_status(200)
#     file_id = res.json_response['fileId']
#     res = api.get_projects_data_mapping_by_file_id(file_id)
#     res.assert_response_status(500)
#     assert res.json_response[
#                 'message'] == "Wrong file status, should be USER_PROJECT_READY. File id {}".format(file_id)


def test_get_user_mapping_download(ac_api_cookie, tmpdir):
    api = FileUploadAPI(ac_api_cookie)
    sample_file = get_data_file("/File_Upload_sample1.xlsx")
    new_sample = copy_file_with_new_name(sample_file, tmpdir, NEW_FILE_NAME)
    payload = {
        "filePath": new_sample,
        "clientId": CLIENT_ID,
        "type": UPLOAD_TYPE
    }
    res = api.upload_file(payload=payload)
    res.assert_response_status(200)
    file_id = res.json_response['fileId']
    res = api.get_users_data_mapping_by_file_id(file_id)
    res.assert_response_status(500)
    assert res.json_response[
                'message'] == "Wrong file status, should be USER_PROJECT_READY. File id {}".format(
        file_id)


def test_get_uploaded_file_sttus(ac_api_cookie, tmpdir):
    api = FileUploadAPI(ac_api_cookie)
    sample_file = get_data_file("/File_Upload_sample1.xlsx")
    new_sample = copy_file_with_new_name(sample_file, tmpdir, NEW_FILE_NAME)
    payload = {
        "filePath": new_sample,
        "clientId": CLIENT_ID,
        "type": UPLOAD_TYPE
    }
    res = api.upload_file(payload=payload)
    res.assert_response_status(200)
    file_id = res.json_response['fileId']
    res = api.get_uploaded_file_status(file_id)
    res.assert_response_status(200)
    assert res.json_response['failedMessage'] == '[null]'
