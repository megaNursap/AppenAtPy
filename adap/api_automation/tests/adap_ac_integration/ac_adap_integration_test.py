import pytest
import allure
import pandas as pd
from dictor import dictor
from adap.api_automation.services_config.worker_ui import WUI
from adap.api_automation.services_config.builder import Builder
from adap.api_automation.utils.data_util import get_user_api_key, save_file_with_content

pytestmark = [pytest.mark.adap_ac_integration, pytest.mark.regression_core, pytest.mark.new_auth, pytest.mark.skipif(
    pytest.env != "integration", reason="Only set up with integration")]

REPORT_COLUMNS = ["date", "adap_contributor_id", "ac_rater_id", "number_of_completed_judgments", "hours_worked",
                  "ac_project_id", "locale", "user_group"]

AC_JOB = pytest.data.predefined_data['ac_adap_jobs'].get(pytest.env)

if AC_JOB:
    AC_JOB = AC_JOB['job_id']

API_KEY = get_user_api_key('test_ac_adap')
_builder = Builder(API_KEY)


@pytest.fixture(scope="module")
def create_ac_job():
    """
    This module creates a simple job with data and sets the
    ac project id to 324 (Figure Eight Integration)
    :return: job id
    """
    _builder.create_simple_job()
    _builder.update_job_settings_v2("job[connect_project_id]=324")
    return _builder.job_id


@pytest.mark.adap_api_uat
def test_set_ac_project_id_valid():
    _builder.create_simple_job()
    res = _builder.update_job_settings_v2("job[connect_project_id]=1")
    res.assert_response_status(200)
    assert dictor(res.json_response, 'connect_project_id') == 1


@pytest.mark.parametrize('scenario, value',
                         [('invalid project id', 0),
                          ('text', 'project'),
                          ('empty', ''),
                          ('special chars', '**&'),
                          ('negative number', -1)])
def test_set_ac_project_id_invalid(scenario, value):
    _builder.create_simple_job()

    res = _builder.update_job_settings({'job[connect_project_id]': value})
    res.assert_response_status(200)
    assert not dictor(res.json_response, 'connect_project_id')


# @pytest.mark.skip(reason="https://appen.atlassian.net/browse/CW-6837")
@pytest.mark.adap_api_uat
def test_set_user_locale(create_ac_job):
    """
    This test sets the user locale on a AC job. It expects an array of locales
    To find get user locales and groups for an AC project make a GET request to:
    https://connect-stage.appen.com/qrp/api/projects/{project_id}'
    """
    _builder.job_id = create_ac_job
    locales = ["eng_USA"]
    res = _builder.update_job_settings_list("locales", locales)
    assert dictor(res.json_response, 'locales') == locales


def test_set_user_groups(create_ac_job):
    """
    This test sets the user groups on a AC job. It expects an array of user groups
    To find get user locales and groups for an AC project make a GET request to:
    https://connect-stage.appen.com/qrp/api/projects/{project_id}'
    """
    _builder.job_id = create_ac_job
    groups = ["ALL USERS"]
    res = _builder.update_job_settings_list('ac_user_groups', groups)
    assert dictor(res.json_response, 'ac_user_groups') == groups


@pytest.mark.adap_api_uat
def test_set_user_group_that_is_not_associated_with_project(create_ac_job):
    _builder.job_id = create_ac_job
    groups = ["TEST GROUP"]
    res = _builder.update_job_settings_list('ac_user_groups', groups)
    assert res.json_response.get('error') == "TEST GROUP is not associated with the AC project"


@pytest.mark.skipif(pytest.env != "integration", reason="Only set up with integration")
def test_set_group_no_project_id():
    try:
        _builder.create_simple_job()
    except ValueError:
        print("Job could not be created. Exiting test...")

    groups = ["ALL USERS"]
    res = _builder.update_job_settings_list('ac_user_groups', groups)
    assert res.json_response.get('error') == 'You must set an AC project ID'


@pytest.mark.skip
def test_set_group_no_feature_flag(create_ac_job):
    no_ac_key = get_user_api_key('test_account')
    _builder.api_key = no_ac_key
    _builder.create_simple_job()
    res = _builder.update_job_settings_v2("job[connect_project_id]=1")
    res.assert_response_status(200)

    groups = ["ALL USERS"]
    res = _builder.update_job_settings_list('ac_user_groups', groups)
    assert res.json_response.get('error') == 'You don’t have access to Appen Connect'


@pytest.mark.adap_api_uat
def test_set_user_groups_and_locale(create_ac_job):
    """
    Only locales OR groups can be set on a job in a request
    """
    _builder.job_id = create_ac_job
    payload = {
        "job": {
            "ac_user_groups": ["ALL USERS"],
            "locales": ["eng_USA"]
        }
    }
    res = _builder.update_job(payload=payload)
    assert res.json_response['error'] == 'Cannot target locales and user groups simultaneously'


@allure.parent_suite('/get_productivity_report:get')
# @pytest.mark.skip(reason="https://appen.atlassian.net/browse/CW-6836")
@pytest.mark.parametrize('scenario, user, expected_status',
                         [('invalid key', 'no_logged_user', 404),
                          ('adap admin', 'test_account', 200),
                          ('org_admin', 'org_admin', 403),
                          ('user on a different team', 'standard_user', 403)])
def test_generate_productivity_metrics_report_access(scenario, user, expected_status):
    _api_key = get_user_api_key(user)
    _wui = WUI(api_key=_api_key)
    res = _wui.generate_productivity_report(AC_JOB)
    res.assert_response_status(expected_status)


@allure.parent_suite('/get_productivity_report:get')
# @pytest.mark.skip(reason="https://appen.atlassian.net/browse/CW-6836")
def test_generate_productivity_metrics_report(tmpdir):
    _wui = WUI(api_key=API_KEY)
    res = _wui.generate_productivity_report(AC_JOB)
    res.assert_response_status(200)
    file_name = tmpdir + '/temp_productivity_report.csv'
    save_file_with_content(file_name, res.content)
    data = pd.read_csv(file_name)
    num_rows = data.shape[0]
    for col in data.columns:
        try:
            assert col in REPORT_COLUMNS
            assert data[col].values[num_rows - 1]
        except KeyError:
            print("{col} is not an expected column name".format(col=col))
