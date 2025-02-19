
from adap.api_automation.utils.data_util import *
from adap.api_automation.services_config.builder import Builder
import time
from adap.data import annotation_tools_cml as data

pytestmark = [pytest.mark.regression_file_upload, pytest.mark.file_upload_ui]

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')
DATA_FILE = get_data_file("/file_upload/sample_data_1row.csv")


@pytest.mark.file_upload_api
def test_create_job_with_mandatory_cml_attributes(app):
    """
    Verify requestor can create job using file_upload cml with mandatory attributes
    <cml:file_upload name="file upload" validates="required"/>
    """

    job = Builder(API_KEY)
    job.create_job_with_csv(DATA_FILE)

    updated_payload = {
        'key': API_KEY,
        'job': {
            'title': "File Upload Test Job - Mandatory Cml",
            'instructions': "mandatory cml attributes",
            'cml': data.file_uplaod_cml_mandatory,
            'project_number': 'PN000112'
        }
    }
    res = job.update_job(payload=updated_payload)
    res.assert_response_status(200)
    assert res.json_response['title'] == "File Upload Test Job - Mandatory Cml"
    assert not res.json_response.get('errors', False)


@pytest.mark.file_upload_api
def test_create_job_with_all_cml_attributes(app):
    """
    Verify requestor can create a job using all available file_upload cml attributes
    <cml:file_upload name="file upload" validates="required" min-size="5" max-size="10.5" allowed-extensions="['JPEG', 'PNG']" />
    """
    job = Builder(API_KEY)
    job.create_job_with_csv(DATA_FILE)

    updated_payload = {
        'key': API_KEY,
        'job': {
            'title': "File Upload Test Job - All Cml",
            'instructions': "all cml attributes",
            'cml': data.file_upload_cml_all,
            'project_number': 'PN000112'
        }
    }
    res = job.update_job(payload=updated_payload)
    res.assert_response_status(200)
    assert res.json_response['title'] == "File Upload Test Job - All Cml"
    assert not res.json_response.get('errors', False)


def test_create_job_invalid_min_max_size(app):
    """
    Verify min-size and max-size cml attributes accept numbers only (including float), but not -ve values
    """
    invalid_min_size_cml = '<cml:file_upload name="file upload" validates="required"  min-size="-1"/>'
    job = Builder(API_KEY)
    job.create_job_with_csv(DATA_FILE)

    updated_payload = {
        'key': API_KEY,
        'job': {
            'title': "File Upload Test job",
            'instructions': "min-size accepts numbers only",
            'cml': invalid_min_size_cml,
            'project_number': 'PN000112'
        }
    }
    res = job.update_job(payload=updated_payload)
    res.assert_response_status(200)
    assert res.json_response == {'errors': ['&lt;cml:file_upload&gt; min-size should have a valid value between 0 and 1024']}

    invalid_max_size_cml = '<cml:file_upload name="file upload" validates="required"  min-size="1" max-size="-10"/>'
    job = Builder(API_KEY)
    job.create_job_with_csv(DATA_FILE)

    updated_payload = {
        'key': API_KEY,
        'job': {
            'title': "File Upload Test job",
            'instructions': "max-size accepts numbers only",
            'cml': invalid_max_size_cml,
            'project_number': 'PN000112'
        }
    }
    res = job.update_job(payload=updated_payload)
    res.assert_response_status(200)
    assert res.json_response == {'errors': ['&lt;cml:file_upload&gt; max-size should have a valid value between 0 and 1024']}


def test_create_job_invalid_size_limit(app):
    """
    Verify min-size and max-size cml attributes cannot be more than 1024MB
    """
    invalid_size_limit_cml = '<cml:file_upload name="file upload" validates="required" min-size="5" max-size="1024.01"/>'
    job = Builder(API_KEY)
    job.create_job_with_csv(DATA_FILE)

    updated_payload = {
        'key': API_KEY,
        'job': {
            'title': "File Upload Test job",
            'instructions': "max-size cannot be more than 1024",
            'cml': invalid_size_limit_cml,
            'project_number': 'PN000112'
        }
    }
    res = job.update_job(payload=updated_payload)
    res.assert_response_status(200)
    assert res.json_response == {'errors': ['&lt;cml:file_upload&gt; max-size should have a valid value between 0 and 1024']}


def test_create_job_min_more_than_max_size(app):
    """
    Verify appropriate error is shown when min-size is more than max-size
    """
    invalid_cml = '<cml:file_upload name="file upload" validates="required" min-size="100.01" max-size="100"/>'
    job = Builder(API_KEY)
    job.create_job_with_csv(DATA_FILE)

    updated_payload = {
        'key': API_KEY,
        'job': {
            'title': "File Upload Test job",
            'instructions': "min-size is more than max-size",
            'cml': invalid_cml,
            'project_number': 'PN000112'
        }
    }
    res = job.update_job(payload=updated_payload)
    res.assert_response_status(200)
    assert res.json_response == {'errors': ['&lt;cml:file_upload&gt; min-size should be less than max-size']}


def test_create_job_same_min_max_size(app):
    """
    Verify appropriate error is shown when both min-size and max-size have the same values
    """
    same_min_max_cml = '<cml:file_upload name="file upload" validates="required" min-size="10" max-size="10"/>'
    job = Builder(API_KEY)
    job.create_job_with_csv(DATA_FILE)

    updated_payload = {
        'key': API_KEY,
        'job': {
            'title': "File Upload Test job",
            'instructions': "both min-size and max-size have the same values",
            'cml': same_min_max_cml,
            'project_number': 'PN000112'
        }
    }
    res = job.update_job(payload=updated_payload)
    res.assert_response_status(200)
    assert res.json_response == {'errors': ['&lt;cml:file_upload&gt; min-size should be less than max-size']}


def test_create_job_only_min_size(app):
    """
    Verify max-size value defaults to 1024MB when only min-size is defined in CML
    """
    only_min_size = '<cml:file_upload name="file upload" validates="required" min-size="100"/>'
    job = Builder(API_KEY)
    job.create_job_with_csv(DATA_FILE)

    updated_payload = {
        'key': API_KEY,
        'job': {
            'title': "File Upload Test job",
            'instructions': "both min-size and max-size have the same values",
            'cml': only_min_size,
            'project_number': 'PN000112'
        }
    }
    res = job.update_job(payload=updated_payload)
    res.assert_response_status(200)

