import datetime
import os
import time

import pytest
from faker import Faker

from adap.api_automation.services_config.quality_flow import QualityFlowApiProject
from adap.api_automation.utils.data_util import get_test_data, get_data_file, count_row_in_file

mark_env = pytest.mark.skipif(not pytest.running_in_preprod_integration, reason="for Integration env")

pytestmark = [pytest.mark.qf_ui,
              pytest.mark.regression_qf,
              mark_env
              ]
username = get_test_data('qf_user_ui', 'email')
password = get_test_data('qf_user_ui', 'password')
team_id = get_test_data('qf_user_ui', 'teams')[0]['id']


@pytest.fixture(scope="module")
def qf_login(app):
    app.user.login_as_customer(username, password)


@pytest.fixture(scope="module")
def new_project(app):
    api = QualityFlowApiProject()
    api.get_valid_sid(username, password)
    _today = datetime.datetime.now().strftime("%Y_%m_%d")

    faker = Faker()

    project_name = f"automation project {_today} {faker.zipcode()} for job test"
    payload = {"name": project_name,
               "description": project_name,
               "unitSegmentType": "UNIT_ONLY"}

    res = api.post_create_project(team_id=team_id, payload=payload)
    assert res.status_code == 200

    response = res.json_response
    data = response.get('data')
    assert data, "Project data has not been found"

    return {
        "project_id": data['id']
    }


@pytest.mark.regression_qf
def test_qf_data_upload_csv_file(app, qf_login, new_project):
    """
    verify user can upload csv file
    """
    app.quality_flow.navigate_to_dataset_page_by_project_id(new_project['project_id'])

    app.verification.text_present_on_page('all data')
    app.verification.text_present_on_page('data group')
    app.verification.text_present_on_page('deleted')

    app.verification.current_url_contains('/dataset')

    sample_file = get_data_file("/authors.csv")

    app.quality_flow.data.all_data.upload_data(sample_file)
    rows_in_file = count_row_in_file(sample_file)

    print("rows_in_file ", rows_in_file)

    time.sleep(20)
    app.navigation.refresh_page()

    dataset_info = app.quality_flow.data.all_data.get_all_units_on_page()
    print("dataset_info ", dataset_info)

    count_new_status = dataset_info[dataset_info['STATUS'] == 'NEW'].shape[0]

    print("count_new_status ", count_new_status)

    assert count_new_status == rows_in_file


@pytest.mark.regression_qf
def test_qf_verify_source_file_batch_number(app, qf_login, new_project):
    """
    verify that column 'Source file batch number displays data - 1'
    """
    app.quality_flow.navigate_to_dataset_page_by_project_id(new_project['project_id'])
    app.quality_flow.data.open_data_tab('all data')

    app.quality_flow.data.all_data.customize_data_table_view(select_fields=['unit'])
    all_units = app.quality_flow.data.all_data.get_all_units_on_page()
    print("all_units ", all_units)
    assert set(all_units['SOURCE FILE BATCH NUMBER'].values) == {'1'}


@pytest.mark.regression_qf
@pytest.mark.parametrize('file_type, file_name',
                         [("csv", "/authors_add.csv"),
                          ("tsv", "/authors.tsv")
                          ])
def test_qf_data_add_more_data_file(app, qf_login, new_project, file_type, file_name):
    """
    verify user can upload tsv file
    verify user can add more data
    """
    app.quality_flow.navigate_to_dataset_page_by_project_id(new_project['project_id'])

    if not app.verification.wait_untill_text_present_on_the_page('Add More Data', max_time=3):
        # no data, upload csv file
        sample_file = get_data_file("/authors.csv")
        app.quality_flow.data.all_data.upload_data(sample_file)
        time.sleep(3)

    dataset_info = app.quality_flow.data.all_data.get_all_units_on_page()
    print("dataset_info ", dataset_info)

    app.navigation.click_link('Add More Data')

    sample_file_tsv = get_data_file(file_name)
    rows_in_file = count_row_in_file(sample_file_tsv)
    print("rows_in_file ", rows_in_file)

    app.quality_flow.data.all_data.upload_data(sample_file_tsv)
    time.sleep(10)
    app.navigation.refresh_page()
    more_data_dataset_info = app.quality_flow.data.all_data.get_all_units_on_page()

    assert more_data_dataset_info['STATUS'].value_counts()['NEW'] == dataset_info['STATUS'].value_counts()[
        'NEW'] + rows_in_file


@pytest.mark.regression_qf
def test_qf_create_data_group(app, qf_login, new_project):
    """
    verify user is able to create data group
    """
    app.quality_flow.navigate_to_dataset_page_by_project_id(new_project['project_id'])

    dataset_info = app.quality_flow.data.all_data.get_all_units_on_page()

    print("dataset_info ", dataset_info)

    sample_file = get_data_file("/authors.csv")
    app.quality_flow.data.all_data.upload_data(sample_file)
    time.sleep(5)
    app.navigation.refresh_page()
    time.sleep(5)

    # if dataset_info['STATUS'].value_counts()['NEW'] == 0:
    #     sample_file = get_data_file("/authors.csv")
    #     app.quality_flow.data.all_data.upload_data(sample_file)
    #     time.sleep(5)
    #     app.navigation.refresh_page()

    app.quality_flow.data.all_data.select_data_units_by(by='UNIT ID', values='1_1')
    app.quality_flow.data.all_data.select_data_units_by(by='UNIT ID', values='1_2')

    app.quality_flow.data.all_data.click_actions_menu('Create a Data Group from Selected Units')
    # todo add verification  - 2 units displayed in modal window
    app.quality_flow.data.data_group.fill_out_data_group_details(name="test", action="Create Data Group")
    time.sleep(5)
    app.quality_flow.data.open_data_tab('data group')

    data_groups = app.quality_flow.data.data_group.get_all_data_groups_on_page()
    print("data_groups ", data_groups)
    assert data_groups.shape[0] == 1
    assert data_groups['NAME'].values[0] == 'test'
    assert data_groups['# ITEMS'].values[0] == '2'


# TODO add verification - data group name is displayed in All data table in DATA GROUP NAME column

@pytest.mark.qf_ui_smoke
def test_qf_delete_data_group(app, qf_login, new_project):
    """
    verify user is able to delete data group
    """
    app.quality_flow.navigate_to_dataset_page_by_project_id(new_project['project_id'])

    app.quality_flow.data.open_data_tab('data group')

    data_groups = app.quality_flow.data.data_group.get_all_data_groups_on_page()
    data_group_name = data_groups['NAME'].values[0]

    app.quality_flow.data.data_group.click_menu_actions_for_data_group_by(menu='Delete Data Group',
                                                                          by='name',
                                                                          value=data_group_name)
    app.quality_flow.data.data_group.confirm_to_delete_data_group()
    app.navigation.refresh_page()
    app.quality_flow.data.open_data_tab('data group')

    app.verification.text_present_on_page('No group items')
    app.verification.text_present_on_page('You can create groups in ALL DATA page')


@pytest.mark.qf_ui_smoke
def test_gf_project_delete_data(app, qf_login, new_project):
    """
    verify: user is able to delete data;
            deleted data displayed in DELETED tab
    """
    app.quality_flow.navigate_to_dataset_page_by_project_id(new_project['project_id'])

    app.quality_flow.data.open_data_tab('all data')

    if not app.verification.wait_untill_text_present_on_the_page('Add More Data', max_time=3):
        # no data, upload csv file
        sample_file = get_data_file("/authors.csv")
        app.quality_flow.data.all_data.upload_data(sample_file)
        time.sleep(3)

    initial_dataset_info = app.quality_flow.data.all_data.get_all_units_on_page()

    app.quality_flow.data.all_data.select_data_units_by(by='UNIT ID', values='1_1')

    app.quality_flow.data.all_data.click_actions_menu('Delete Selected Units')
    app.navigation.click_link('Yes, I Want to Delete These Units')
    app.navigation.refresh_page()
    time.sleep(4)

    updated_dataset_info = app.quality_flow.data.all_data.get_all_units_on_page()
    assert updated_dataset_info.shape[0] == initial_dataset_info.shape[0] - 1
    app.quality_flow.data.open_data_tab('deleted')

    all_deleted = app.quality_flow.data.deleted.get_all_deleted_units_on_page()
    print("all_deleted ", all_deleted)
    assert '1_1' in all_deleted['UNIT ID'].values, "The DataFrame does not contain ID == 1_1"


@pytest.mark.qf_ui_smoke
@pytest.mark.dependency(depends=["test_gf_project_delete_data"])
def test_qf_return_units_to_all_data(app, qf_login, new_project):
    """
    verify user is able to return deleted units to all data tab
    """
    app.quality_flow.navigate_to_dataset_page_by_project_id(new_project['project_id'])

    app.quality_flow.data.open_data_tab('deleted')

    app.quality_flow.data.deleted.select_all_units()
    app.navigation.click_link("Return units to All Data")
    time.sleep(10)

    app.navigation.refresh_page()

    app.verification.text_present_on_page("No deleted items")
    app.verification.text_present_on_page("You can delete items in ALL DATA page")


@pytest.mark.qf_uat_ui
@pytest.mark.parametrize('file_type, file_name, message',
                         [
                             ("blank headers", "/upload_data_files/blank_headers.csv",
                              "Header contains empty columns."),
                             ("duplicate headers", "/upload_data_files/dup_headers.csv",
                              "Header contains duplicate columns."),
                             ("wrong file format - json", "/authors.json",
                              "Error: wrong file type"),
                             ("wrong file format - ods", "/authors.ods",
                              "Error: wrong file type"),
                             ("wrong file format - xls", "/authors.xls",
                              "Error: wrong file type"),
                             ("wrong file format - xlsx", "/authors.xlsx",
                              "Error: wrong file type")
                         ])
def test_qf_data_upload_bad_files(app, qf_login, new_project, file_type, file_name, message):
    app.quality_flow.navigate_to_dataset_page_by_project_id(new_project['project_id'])

    app.quality_flow.data.open_data_tab('all data')
    time.sleep(5)

    dataset_info = app.quality_flow.data.all_data.get_all_units_on_page()

    if app.verification.wait_untill_text_present_on_the_page('Add More Data', max_time=3):
        app.navigation.click_link('Add More Data')

    sample_file = get_data_file(file_name)
    print("sample_file ", sample_file)
    app.quality_flow.data.all_data.upload_data(sample_file)

    app.navigation.refresh_page()
    time.sleep(5)

    current_dataset_info = app.quality_flow.data.all_data.get_all_units_on_page()

    assert dataset_info.shape[0] == current_dataset_info.shape[0]


@pytest.mark.qf_uat_ui
def test_qf_verify_filter_options(app, qf_login, new_project):
    app.quality_flow.navigate_to_dataset_page_by_project_id(new_project['project_id'])

    all_filters = app.quality_flow.data.all_data.get_all_filters()

    assert all_filters == ['Unit',
                           'Unit ID',
                           'Replica',
                           'Dataset Row Type',
                           'Status',
                           'Source File Batch Number',
                           'Row Number',
                           'MD5 Hash',
                           'Created At',
                           'Unit Segment Type',
                           'Question ID',
                           'Source',
                           'Author',
                           'Countries_Active',
                           'Major_Works'
                           ]


@pytest.mark.qf_uat_ui
def test_qf_filter_by_unit_id(app, qf_login, new_project):
    """
    verify user is able to use filter by unit id
    verify user is able to remove filters
    """
    app.quality_flow.navigate_to_dataset_page_by_project_id(new_project['project_id'])
    initial_units_on_page = app.quality_flow.data.all_data.get_all_units_on_page()
    initial_num_rows = initial_units_on_page.shape[0]
    app.quality_flow.data.all_data.select_filter('unit', 'Unit ID', 'Not Equal', '1_1', 'Apply')

    app.verification.text_present_on_page('1 Filter')

    filtered_units_on_page = app.quality_flow.data.all_data.get_all_units_on_page()
    filtered_num_rows = filtered_units_on_page.shape[0]

    assert len(filtered_units_on_page.loc[filtered_units_on_page['UNIT ID'] == '1_1']) == 0
    assert (initial_num_rows - filtered_num_rows) == 1

    app.quality_flow.data.all_data.remove_current_filter()
    app.verification.text_present_on_page('1 Filter', is_not=False)

    remove_filtered_units_on_page = app.quality_flow.data.all_data.get_all_units_on_page()
    remove_filtered_num_rows = remove_filtered_units_on_page.shape[0]

    assert remove_filtered_num_rows == initial_num_rows

# TODO expend test coverage for filter
# TODO Same file can not be uploaded repeatedly. - add test
