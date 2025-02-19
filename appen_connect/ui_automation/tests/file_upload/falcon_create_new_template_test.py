"""
https://appen.atlassian.net/browse/QED-2040
https://appen.atlassian.net/browse/QED-2041
"""
import time

from adap.api_automation.utils.data_util import *
from adap.ui_automation.utils.js_utils import inner_scroll_to_element, scroll_to_page_bottom
from appen_connect.ui_automation.service_config.project.project_helper import tomorrow_date
from adap.ui_automation.utils.selenium_utils import find_elements

pytestmark = [pytest.mark.regression_ac_file_upload, pytest.mark.regression_ac, pytest.mark.ac_file_upload]

USER_NAME = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
faker = Faker()
random_prefix = faker.zipcode()

NEW_FILE_NAME = "file_upload_{}.xlsx".format(random_prefix)
NEW_FILE_NAME_2 = "new_file_upload_{}.xlsx".format(random_prefix)
TEMPLATE_NAME = "create_new_template_" + random_prefix


@pytest.fixture(scope="module")
def login(app):
    app.ac_user.login_as(user_name=USER_NAME, password=PASSWORD)
    app.navigation.click_link('Partner Home')
    # app.navigation.click_link('Falcon')
    app.navigation.click_link('File Upload')
    app.navigation.click_btn('File Upload')
    app.navigation.switch_to_frame("page-wrapper")
    app.driver.implicitly_wait(2)


@pytest.mark.dependency()
def test_step1_file_selection_falcon(app, login, tmpdir):
    app.navigation.click_btn("Upload New File")
    sample_file = get_data_file("/File_Upload_sample1.xlsx")

    new_sample = copy_file_with_new_name(sample_file, tmpdir, NEW_FILE_NAME)
    assert app.file_upload.get_uploaded_files_on_selection_page() == []

    app.file_upload.enter_data({
        "Client": "Bluebird",
        "Upload Type": "Productivity Data (Invoicing)",
        "Upload File": new_sample
    })
    assert app.file_upload.get_uploaded_files_on_selection_page() == [NEW_FILE_NAME]

    scroll_to_page_bottom(app.driver)
    app.navigation.click_btn('Next: Template')


@pytest.mark.dependency(depends=["test_step1_file_selection_falcon"])
def test_step2_create_new_template(app, login):
    app.file_upload.open_toggle('CREATE NEW TEMPLATE')
    app.verification.button_is_disable('Next: Column Connection')
    app.file_upload.enter_data({
        "Template name": TEMPLATE_NAME,
        "Timezone": "US/Pacific"
    })

    scroll_to_page_bottom(app.driver)
    app.navigation.click_btn("Next: Column Connection")


@pytest.mark.dependency(depends=["test_step2_create_new_template"])
def test_step3_column_connection(app, login):
    time.sleep(15)
    assert app.file_upload.count_items_in_specific_status("Pending") == 5
    assert app.file_upload.count_items_in_specific_status("Complete") == 0
    app.file_upload.edit_column_connection('Project Connection')
    app.verification.text_present_on_page('Edit Identifiers')
    app.verification.text_present_on_page('Project Connection')
    app.verification.text_present_on_page('FILE HAS AC IDS')
    app.verification.text_present_on_page('FILE HAS CLIENT IDS')
    app.verification.text_present_on_page('FILE HAS NO IDS')


@pytest.mark.dependency(depends=["test_step3_column_connection"])
def test_project_connection_required_fields(app, login):
    app.navigation.click_btn("Save & Close")
    app.verification.text_present_on_page('Required Field')
    app.file_upload.open_toggle("FILE HAS CLIENT IDS")
    app.navigation.click_btn("Save & Close")
    app.verification.text_present_on_page('Required Field')
    app.file_upload.open_toggle("FILE HAS NO IDS")
    app.navigation.click_btn("Save & Close")
    app.verification.text_present_on_page('Required Field')


@pytest.mark.dependency(depends=["test_project_connection_required_fields"])
def test_edit_project_connection_file_has_acids(app, login):
    app.file_upload.open_toggle("FILE HAS AC IDS")
    app.file_upload.enter_data({
        "COLUMN WITH AC PROJECT ID": "queue"
    })
    app.navigation.click_btn("Save & Close")
    app.verification.text_present_on_page("Column with AC ID: queue")
    assert app.file_upload.count_items_in_specific_status("Pending") == 4
    assert app.file_upload.count_items_in_specific_status("Complete") == 1


@pytest.mark.dependency(depends=["test_edit_project_connection_file_has_acids"])
def test_edit_project_connection_file_has_client_ids(app, login):
    app.file_upload.edit_column_connection('Project Connection')
    app.file_upload.open_toggle("FILE HAS CLIENT IDS")
    app.file_upload.enter_data({
        "COLUMN NAME": "name"
    })
    app.navigation.click_btn("Save & Close")
    app.file_upload.edit_column_connection('Project Connection')
    app.file_upload.open_toggle("FILE HAS CLIENT IDS")
    app.file_upload.enter_data({
        "COLUMN NAME": "productivity"
    })
    app.navigation.click_btn("Save & Close")
    app.verification.text_present_on_page("Column(s) with client ID(s): name, productivity")
    assert app.file_upload.count_items_in_specific_status("Pending") == 4
    assert app.file_upload.count_items_in_specific_status("Edited") == 1


@pytest.mark.dependency(depends=["test_edit_project_connection_file_has_client_ids"])
def test_user_connection_required_fields(app, login):
    app.file_upload.edit_column_connection('User Connection')
    app.verification.text_present_on_page('Edit Identifiers')
    app.verification.text_present_on_page('User Connection')
    app.verification.text_present_on_page('FILE HAS AC USER IDS')
    app.verification.text_present_on_page('FILE HAS CLIENT IDS')
    app.navigation.click_btn("Save & Close")
    app.verification.text_present_on_page('Required Field')
    app.file_upload.open_toggle("FILE HAS CLIENT IDS")
    app.navigation.click_btn("Save & Close")
    app.verification.text_present_on_page('Required Field')


@pytest.mark.dependency(depends=["test_user_connection_required_fields"])
def test_edit_user_connection_file_has_client_ids(app, login):
    app.file_upload.open_toggle("FILE HAS CLIENT IDS")
    app.file_upload.enter_data({
        "COLUMN NAME": "name"
    })
    app.navigation.click_btn("Save & Close")
    app.verification.text_present_on_page("Column(s) with client ID(s): name")
    app.file_upload.edit_column_connection('User Connection')
    app.file_upload.open_toggle("FILE HAS CLIENT IDS")
    app.file_upload.enter_data({
        "COLUMN NAME": "day"
    })
    app.navigation.click_btn("Save & Close")
    app.verification.text_present_on_page("Column(s) with client ID(s): name, day")
    assert app.file_upload.count_items_in_specific_status("Pending") == 3
    assert app.file_upload.count_items_in_specific_status("Edited") == 2



@pytest.mark.dependency(depends=["test_edit_user_connection_file_has_client_ids"])
def test_date_of_work_required_fields(app, login):
    app.file_upload.edit_column_connection('Date of Work')
    app.verification.text_present_on_page('Edit Identifiers')
    app.verification.text_present_on_page('FILE HAS DATES')
    app.verification.text_present_on_page('FILE HAS NO DATES')
    app.navigation.click_btn("Save & Close")
    app.verification.text_present_on_page('Field is required')
    app.file_upload.open_toggle("FILE HAS NO DATES")
    app.navigation.click_btn("Save & Close")
    app.verification.text_present_on_page('Field is required')


@pytest.mark.dependency(depends=["test_date_of_work_required_fields"])
def test_edit_date_of_work_file_has_dates(app, login):
    app.file_upload.open_toggle("FILE HAS DATES")
    app.file_upload.enter_data({
        "column with date of work date": "user_id"
    })
    app.navigation.click_btn("Save & Close")
    app.verification.text_present_on_page("Column with days of work: user_id")
    assert app.file_upload.count_items_in_specific_status("Pending") == 2
    assert app.file_upload.count_items_in_specific_status("Complete") == 1
    assert app.file_upload.count_items_in_specific_status("Edited") == 2

#################################################################################

@pytest.mark.dependency(depends=["test_edit_date_of_work_file_has_dates"])
def test_edit_date_of_work_file_has_no_dates(app, login):
    app.file_upload.edit_column_connection('Date of Work')
    app.file_upload.open_toggle("FILE HAS NO DATES")
    app.file_upload.enter_data({
        "select a date": tomorrow_date()
    })
    app.navigation.click_btn("Save & Close")
    assert app.file_upload.count_items_in_specific_status("Pending") == 2
    assert app.file_upload.count_items_in_specific_status("Edited") == 3


#################################################################################
@pytest.mark.dependency(depends=["test_edit_date_of_work_file_has_no_dates"])
def test_edit_time_worked_file_had_no_data(app, login):
    app.file_upload.edit_column_connection('Production Time')
    app.file_upload.open_toggle("FILE HAS NO DATA")
    app.verification.text_present_on_page("The file does not contain production time data")
    app.navigation.click_btn("Save & Close")
    app.verification.text_present_on_page('The file does not contain production time data')


@pytest.mark.dependency(depends=["test_edit_date_of_work_file_has_no_dates"])
def test_time_worked_required_fields(app, login):
    app.file_upload.edit_column_connection('Production Time')
    app.verification.text_present_on_page('Edit Identifiers')
    app.file_upload.open_toggle("TIME WORKED")
    app.verification.text_present_on_page("TIME WORKED")
    app.verification.text_present_on_page('Add a fixed amount per row.')
    app.verification.text_present_on_page('FILE HAS NO DATA')
    app.verification.button_is_disable("Save & Close")
    app.file_upload.check_checkbox_for_time_worked("Calculate data from cell values, using")
    app.navigation.click_btn("Save & Close")
    app.verification.text_present_on_page('Field is required')


@pytest.mark.dependency(depends=["test_time_worked_required_fields"])
def test_edit_time_worked_file_has_data_math(app, login):
    app.file_upload.enter_data({
        "column with Production Time": "day",
        "time unit": "Hour"
    })
    app.navigation.click_btn("Save & Close")
    assert app.file_upload.count_items_in_specific_status("Pending") == 1
    assert app.file_upload.count_items_in_specific_status("Complete") == 1
    assert app.file_upload.count_items_in_specific_status("Edited") == 3


@pytest.mark.dependency(depends=["test_edit_time_worked_file_has_data_math"])
def test_edit_time_worked_choose_if_total_option(app, login):
    app.file_upload.edit_column_connection('Production Time')
    app.file_upload.check_checkbox_for_time_worked("If total > ")
    app.navigation.click_btn("Save & Close")
    app.verification.text_present_on_page('Field is required')
    app.file_upload.enter_data({
        "Business value": "1",
        "Exceed value": "1"
    })
    app.navigation.click_btn("Save & Close")
    assert app.file_upload.count_items_in_specific_status("Pending") == 1
    assert app.file_upload.count_items_in_specific_status("Edited") == 4



#################################################################################
@pytest.mark.dependency(depends=["test_edit_time_worked_choose_if_total_option"])
def test_units_of_work_completed_required_fields(app, login):
    app.verification.button_is_disable("Next: Project Mapping")
    app.file_upload.edit_column_connection('Units of Work Completed')
    app.verification.text_present_on_page('Edit Identifiers')
    app.verification.text_present_on_page("Units of Work Completed")
    app.verification.text_present_on_page('FILE HAS DATA')
    app.verification.text_present_on_page('FILE HAS NO DATA')
    app.verification.button_is_disable('Save & Close')
    app.file_upload.check_checkbox_for_units_of_work_complete("Calculate data from cell values.")
    app.navigation.click_btn("Save & Close")
    app.verification.text_present_on_page("Field is required")


@pytest.mark.dependency(depends=["test_units_of_work_completed_required_fields"])
def test_edit_unit_of_work_completed(app, login):
    app.file_upload.open_toggle("FILE HAS DATA")
    app.file_upload.enter_data({
        "Column with Units of Work Completed": "day"
    })
    app.navigation.click_btn("Save & Close")
    assert not app.verification.button_is_disable("Next: Project Mapping")
    assert app.file_upload.count_items_in_specific_status("Complete") == 1
    assert app.file_upload.count_items_in_specific_status("Edited") == 4


@pytest.mark.dependency(depends=["test_edit_unit_of_work_completed"])
def test_edit_unit_of_work_file_has_no_dates(app, login):
    app.file_upload.edit_column_connection('Units of Work Completed')
    app.file_upload.open_toggle("FILE HAS NO DATA")
    app.navigation.click_btn("Save & Close")
    assert app.file_upload.count_items_in_specific_status("Complete") == 0
    assert app.file_upload.count_items_in_specific_status("Edited") == 5


@pytest.mark.dependency(depends=["test_edit_unit_of_work_file_has_no_dates"])
def test_edit_advanced(app, login):
    scroll_to_page_bottom(app.driver)
    time.sleep(1)
    app.file_upload.edit_column_connection('Advanced Data Connection')
    app.file_upload.select_value_for_advanced("total_review_time", "user_id")
    app.file_upload.select_value_for_advanced("queue", "user_id")
    app.navigation.click_btn("Save & Close")
    app.verification.text_present_on_page("Please fix the duplicates. Select a unique partner data columns for each CSV header.")
    app.navigation.click_btn("Cancel")
    app.navigation.click_btn("Next: Project Mapping")
    time.sleep(5)


@pytest.mark.dependency(depends=["test_edit_advanced"])
def test_create_template_with_existing_name(app, login, tmpdir):
    # app.driver.switch_to.default_content()
    # app.navigation.click_link('Partner Home')
    # email = find_elements(app.driver, '//input[@name="username"]')
    # if len(email) > 0:
    #     app.ac_user.login_as(user_name=USER_NAME, password=PASSWORD)
    #     app.navigation.click_link('Partner Home')
    #
    # app.navigation.click_link('Falcon')
    app.navigation.refresh_page()
    # app.navigation.click_link('File Upload')
    app.navigation.switch_to_frame("page-wrapper")
    # app.navigation.click_btn('File Upload')
    app.navigation.click_btn("Upload New File")
    sample_file = get_data_file("/File_Upload_sample1.xlsx")

    new_sample = copy_file_with_new_name(sample_file, tmpdir, NEW_FILE_NAME_2)
    assert app.file_upload.get_uploaded_files_on_selection_page() == []

    app.file_upload.enter_data({
        "Client": "Bluebird",
        "Upload Type": "Productivity Data (Invoicing)",
        "Upload File": new_sample
    })
    assert app.file_upload.get_uploaded_files_on_selection_page() == [NEW_FILE_NAME_2]

    scroll_to_page_bottom(app.driver)
    app.navigation.click_btn('Next: Template')

    app.file_upload.open_toggle('CREATE NEW TEMPLATE')
    app.verification.button_is_disable('Next: Column Connection')
    app.file_upload.enter_data({
        "Template name": "automate new template name test",
        "Timezone": "US/Pacific"
    })

    scroll_to_page_bottom(app.driver)
    app.navigation.click_btn("Next: Column Connection")
    app.verification.text_present_on_page("This template name already exists.")

