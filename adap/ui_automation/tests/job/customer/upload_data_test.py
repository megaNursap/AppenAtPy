import time
import ast

import allure

from adap.api_automation.services_config.builder import Builder as JobAPI
from adap.api_automation.utils.data_util import *
from adap.ui_automation.utils.pandas_utils import collect_data_from_ui_table, collect_data_from_file

pytestmark = [
    pytest.mark.regression_core,
    pytest.mark.adap_ui_uat,
    pytest.mark.adap_uat
]


@pytest.mark.ui_smoke
@pytest.mark.ui_uat
@pytest.mark.fed_ui_smoke
@pytest.mark.fed_ui
# @allure.issue("https://appen.atlassian.net/browse/ADAP-1910", "BUG ADAP-1910")
@pytest.mark.parametrize('file_type, file_name',
                         [
                             ("csv", "/authors.csv"),
                             ("json", "/sample_data.json")
                         ])
def test_upload_data_from_file(app_test, file_type, file_name):
    """
    Customer is able to upload data to a job
    """
    api_key = get_user_api_key('test_ui_account')
    email = get_user_email('test_ui_account')
    password = get_user_password('test_ui_account')

    resp = JobAPI(api_key).create_job()
    job_id = resp.json_response['id']
    assert resp.status_code == 200, "Job was not created!"

    app_test.user.login_as_customer(user_name=email, password=password)

    app_test.mainMenu.jobs_page()
    app_test.job.open_job_with_id(job_id)

    app_test.job.open_tab("DATA")
    sample_file = get_data_file(file_name)
    app_test.job.data.upload_file(sample_file)

    app_test.job.data.sort_data_by_column("Unit id", "asc")

    row_num_file = count_row_in_file(sample_file)
    rows_in_job = app_test.job.data.get_number_of_units_on_page()
    assert row_num_file == rows_in_job

    data_ui = collect_data_from_ui_table(app_test.driver)
    print("data ui is:", data_ui)
    data_file = collect_data_from_file(sample_file)
    print("data file is:", data_file)

    # app_test.verification.assert_data_frame_equals(data_file, data_ui)


@pytest.mark.ui_uat
@pytest.mark.fed_ui_smoke
@pytest.mark.fed_ui
def test_upload_additional_data_to_job(app_test):
    """
    Customer is able to upload additional data to a job
    """
    api_key = get_user_api_key('test_ui_account')
    email = get_user_email('test_ui_account')
    password = get_user_password('test_ui_account')

    resp = JobAPI(api_key).create_job()
    job_id = resp.json_response['id']
    assert resp.status_code == 200, "Job was not created!"

    app_test.user.login_as_customer(user_name=email, password=password)

    app_test.mainMenu.jobs_page()
    app_test.job.open_job_with_id(job_id)

    app_test.job.open_tab("DATA")
    sample_file = get_data_file('/authors.csv')
    data_file = collect_data_from_file(sample_file)

    sample_file_add = get_data_file('/authors_add.csv')
    data_file1 = collect_data_from_file(sample_file_add)

    app_test.job.data.upload_file(sample_file)

    app_test.navigation.click_link("Add More Data")
    app_test.job.data.upload_file(sample_file_add)

    time.sleep(4)
    app_test.navigation.refresh_page()

    app_test.job.data.sort_data_by_column("Unit id", "asc")
    data_ui = collect_data_from_ui_table(app_test.driver)
    print("data ui is:", data_ui)
    all_data = data_file.append(data_file1)
    all_data.reset_index(inplace = True)
    all_data.drop('index', axis=1, inplace=True)
    print("data ui is:", all_data)

    # Data_ui has additional row with 0  None  None None , need to fix
    app_test.verification.assert_data_frame_equals(all_data, data_ui)



@pytest.mark.ui_uat
@pytest.mark.fed_ui_smoke
@pytest.mark.fed_ui
def test_split_column_ui(app_test):
    """
    Customer is able to split column
    """
    api_key = get_user_api_key('test_ui_account')
    email = get_user_email('test_ui_account')
    password = get_user_password('test_ui_account')

    resp = JobAPI(api_key).create_job()
    job_id = resp.json_response['id']
    assert resp.status_code == 200, "Job was not created!"

    app_test.user.login_as_customer(user_name=email, password=password)

    app_test.mainMenu.jobs_page()
    app_test.job.open_job_with_id(job_id)

    app_test.job.open_tab("DATA")
    sample_file = get_data_file('/authors.csv')

    app_test.job.data.upload_file(sample_file)

    app_test.navigation.refresh_page()

    before_data_ui = collect_data_from_ui_table(app_test.driver)
    print("data ui is:", before_data_ui)

    app_test.navigation.click_link('Split column')
    app_test.job.data.split_column('major_works', '|')
    app_test.navigation.refresh_page()

    after_data_ui = collect_data_from_ui_table(app_test.driver)
    print("after data ui is:", after_data_ui)

    for i, row in enumerate(before_data_ui['major_works']):
        assert row.split('|') == ast.literal_eval(after_data_ui['major_works'][i])


