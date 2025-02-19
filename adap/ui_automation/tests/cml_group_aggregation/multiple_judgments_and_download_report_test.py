"""
https://appen.atlassian.net/browse/QED-1271
create CML group aggregation job, annotate it and validate value in report
"""
import time
import pytest
import json
from adap.api_automation.utils.data_util import *
from adap.e2e_automation.services_config.job_api_support import generate_job_link
from adap.api_automation.services_config.builder import Builder as JobAPI
from adap.data import annotation_tools_cml as data
from adap.ui_automation.utils.selenium_utils import create_screenshot
USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')
REQUESTORS = ['test_ui_account', 'test_account']

pytestmark = [pytest.mark.fed_ui, pytest.mark.cml_group_aggregation]


@pytest.fixture(scope="module")
def tx_job(app):
    job = JobAPI(API_KEY)
    job.create_job_with_cml(data.cml_group_aggregation)
    job_id = job.job_id
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)
    app.job.open_tab("DATA")
    data_file = get_data_file('/cml_group_aggregation/group_aggregation.csv')
    app.job.data.upload_file(data_file)

    if pytest.env == 'fed':
        app.job.open_action("Settings")
        app.navigation.click_link("Select Contributor Channels")
        app.job.select_hosted_channel_by_index(save=True)

    job.launch_job()
    job = JobAPI(API_KEY, job_id=job_id)
    job.wait_until_status('running', 80)
    res = job.get_json_job_status()
    res.assert_response_status(200)
    app.user.logout()
    return job_id


@pytest.mark.dependency()
def test_multiple_judgements_for_aggregation(app_test, tx_job):
    for requester in REQUESTORS:
        job_link = generate_job_link(tx_job, API_KEY, pytest.env)
        app_test.user.login_as_customer(user_name=get_user_email(requester), password=get_user_password(requester))
        app_test.navigation.open_page(job_link)
        app_test.user.close_guide()
        create_screenshot(app_test.driver, 'tedst2')
        first_name_input = app_test.group_aggregation.get_input_text_field('output_first_name')
        create_screenshot(app_test.driver, 'tedst2')
        last_name_input = app_test.group_aggregation.get_input_text_field('output_last_name')
        assert len(first_name_input) == 5
        assert len(last_name_input) == 5
        for i in range(0, 5):
            first_name_input[i].send_keys("first" + str(i))
            time.sleep(1)
            last_name_input[i].send_keys("last" + str(i))
            time.sleep(1)
        app_test.group_aggregation.submit_page()
        app_test.verification.text_present_on_page('There is no work currently available in this task.')
        if pytest.env != 'fed':
            app_test.user.task.logout()


@pytest.mark.dependency(depends=["test_multiple_judgements_for_aggregation"])
def test_verify_reports_and_confidence(app_test, tx_job):
    app_test.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    app_test.mainMenu.jobs_page()
    app_test.job.open_job_with_id(tx_job)

    for report_type in ['Full', 'Aggregated']:
        app_test.job.open_tab("RESULTS")
        app_test.job.results.download_report(report_type, tx_job)
        file_name_zip = "/" + app_test.job.results.get_file_report_name(tx_job, report_type)
        full_file_name_zip = app_test.temp_path_file + file_name_zip

        unzip_file(full_file_name_zip)
        csv_name = str(full_file_name_zip)[:-4]

        _df = pd.read_csv(csv_name)
        assert 'output_first_name' in _df.columns
        assert 'output_last_name' in _df.columns
        assert 'group1' in _df.columns

        for i in range(0, 5):
            output_first_name = _df['output_first_name'][i]
            output_last_name = _df['output_last_name'][i]
            json_value = json.loads(_df['group1'][i])
            if report_type == 'Full':
            #     first_name = output_first_name.split('\n')
            #     last_name = output_last_name.split('\n')
            #     assert len(first_name) == 3
            #     assert len(last_name) == 3
            #     for name_index in range(0, 3):
            #         first_name[name_index] in ['first0', 'first1', 'first2', 'first3', 'first4']
            #         last_name[name_index] in ['last0', 'last1', 'last2', 'last3', 'last4']
            #     assert _df['_trusted_judgments'][i] == 3
            #     if len(json_value) == 1:
            #         assert 1.0 == json_value[0].get('confidence')
            #     elif len(json_value) == 2:
            #         assert json_value[0].get('confidence') in [0.6667, 0.3333]
            #         assert json_value[1].get('confidence') in [0.6667, 0.3333]
            #     elif len(json_value) == 3:
            #         assert 0.3333 == json_value[0].get('confidence')
            # else:
                assert output_first_name in ['first0', 'first1', 'first2', 'first3', 'first4']
                assert output_last_name in ['last0', 'last1', 'last2', 'last3', 'last4']
                assert _df['_trusted_judgments'][i] == 1
                assert 1.0 == json_value[0].get('confidence')

        os.remove(csv_name)
        os.remove(full_file_name_zip)


@pytest.mark.prod_bug
@pytest.mark.dependency(depends=["test_verify_reports_and_confidence"])
def test_verify_contributors_info(app_test, tx_job):
    """
    prod bug https://appen.atlassian.net/browse/ADAP-1018
    verify no duplicated judgements per unit
    """
    app_test.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    app_test.mainMenu.jobs_page()
    app_test.job.open_job_with_id(tx_job)

    app_test.job.open_tab("DATA")

    units = app_test.job.data.find_all_units_with_status('judgable')
    first_unit = units['unit id'][0]
    app_test.job.data.open_unit_by_id(first_unit)

    app_test.annotation.activate_iframe_by_name('unit_page')
    app_test.navigation.click_link('Show Contributor Info')

    contributors = app_test.job.data.get_contributor_ids_for_unit()
    assert len(contributors) == len(set(contributors)), "Found duplicated judgements"
