"""
https://appen.atlassian.net/browse/QED-2550
"""
import time
from adap.api_automation.utils.data_util import *
from adap.ui_automation.utils.js_utils import scroll_to_page_bottom
import datetime

pytestmark = [pytest.mark.ac_ui_uat,
              pytest.mark.regression_ac,
              pytest.mark.ac_file_upload,
              pytest.mark.regression_ac_file_upload]

USER_NAME = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
faker = Faker()
random_prefix = faker.zipcode()

NEW_FILE_NAME = "file_upload_{}.xlsx".format(random_prefix)


@pytest.fixture(scope="module")
def login(app):
    app.ac_user.login_as(user_name=USER_NAME, password=PASSWORD)
    app.navigation.click_link('Partner Home')
    # app.navigation.click_link('Falcon')
    app.navigation.click_link('File Upload')
    app.navigation.click_btn('File Upload')
    app.navigation.switch_to_frame("page-wrapper")


@pytest.mark.dependency()
def test_open_file_upload_page_new(app, login):
    app.verification.text_present_on_page("File Upload")
    app.verification.text_present_on_page("FILE NAME")
    app.verification.text_present_on_page("DATE OF WORK")
    app.verification.text_present_on_page("PROJECTS")
    app.verification.text_present_on_page("UPLOAD TYPE")
    app.verification.text_present_on_page("CREATED AT")
    app.verification.text_present_on_page("STATUS")


@pytest.mark.dependency(depends=["test_open_file_upload_page_new"])
def test_upload_new_quality_file(app, login):
    app.navigation.click_btn("Upload New File")
    app.verification.text_present_on_page("File Selection")
    app.verification.text_present_on_page("Template")


@pytest.mark.dependency(depends=["test_upload_new_quality_file"])
def test_file_selection_for_quality(app, login, tmpdir):
    sample_file = get_data_file("/quality_file_upload_data.xlsx")
    new_sample = copy_file_with_new_name(sample_file, tmpdir, NEW_FILE_NAME)
    assert app.file_upload.get_uploaded_files_on_selection_page() == []

    app.file_upload.enter_data({
        "Client": "Falcon",
        "Upload Type": "Quality Data",
        "Upload File": new_sample
    })

    assert app.file_upload.get_uploaded_files_on_selection_page() == [NEW_FILE_NAME]
    time.sleep(5)
    scroll_to_page_bottom(app.driver)
    app.navigation.click_btn('Next: Template')


@pytest.mark.dependency(depends=["test_file_selection_for_quality"])
def test_create_new_template(app, login):
    app.file_upload.open_toggle('CREATE NEW TEMPLATE')
    app.file_upload.enter_data({
        "Template name": generate_random_string(6),
        "Timezone": "US/Pacific"

    })
    app.navigation.click_btn("Next: Column Connection")


@pytest.mark.dependency(depends=["test_create_new_template"])
def test_edit_project_connection(app, login):
    time.sleep(5)
    assert app.file_upload.count_items_in_specific_status("Pending") == 5
    assert app.file_upload.count_items_in_specific_status("Complete") == 0

    app.file_upload.edit_column_connection('Project Connection')
    app.verification.text_present_on_page('Edit Identifiers')
    app.verification.text_present_on_page('Project Connection')
    app.verification.text_present_on_page('FILE HAS AC IDS')
    app.verification.text_present_on_page('FILE HAS CLIENT IDS')
    app.verification.text_present_on_page('FILE HAS NO IDS')
    app.navigation.click_btn("Save & Close")
    app.verification.text_present_on_page('Required Field')
    app.file_upload.open_toggle("FILE HAS CLIENT IDS")
    app.navigation.click_btn("Save & Close")
    app.verification.text_present_on_page('Required Field')
    app.file_upload.open_toggle("FILE HAS NO IDS")
    app.file_upload.search_project_alias("Falcon VTX", "Falcon VTX 2018 - French (France) - Annotation")
    app.navigation.click_btn('Save & Close')
    app.verification.text_present_on_page("AC project: Falcon VTX 2018 - French (France) - Annotation 215")
    assert app.file_upload.count_items_in_specific_status("Pending") == 4
    assert app.file_upload.count_items_in_specific_status("Complete") == 1


@pytest.mark.dependency(depends=["test_edit_project_connection"])
def test_edit_user_connection(app, login):
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

    app.file_upload.enter_data({
        "COLUMN NAME": "rater_id"
    })
    app.navigation.click_btn('Save & Close')
    app.verification.text_present_on_page("Column(s) with client ID(s): rater_id")
    assert app.file_upload.count_items_in_specific_status("Pending") == 3
    assert app.file_upload.count_items_in_specific_status("Complete") == 2


@pytest.mark.dependency(depends=["test_edit_user_connection"])
def test_edit_date_of_work(app, login):
    app.file_upload.edit_column_connection('Date of Work')
    app.verification.text_present_on_page('Edit Identifiers')
    app.verification.text_present_on_page('FILE HAS DATES')
    app.verification.text_present_on_page('FILE HAS NO DATES')
    app.navigation.click_btn("Save & Close")
    app.verification.text_present_on_page('Field is required')
    app.file_upload.open_toggle("FILE HAS NO DATES")
    app.navigation.click_btn("Save & Close")
    app.verification.text_present_on_page('Field is required')

    past_date = (datetime.date.today() - datetime.timedelta(days=30)).strftime("%m/%d/%Y")
    app.file_upload.enter_data({
        "select a date": past_date
    })
    app.navigation.click_btn("Save & Close")
    assert app.file_upload.count_items_in_specific_status("Pending") == 2
    assert app.file_upload.count_items_in_specific_status("Complete") == 3


@pytest.mark.dependency(depends=["test_edit_date_of_work"])
def test_edit_quality_numerator(app, login):
    app.file_upload.edit_column_connection('Quality Numerator')
    app.file_upload.check_checkbox_for_time_worked("Calculate data from cell values.")
    app.navigation.click_btn("Save & Close")
    app.verification.text_present_on_page('Field is required')

    app.file_upload.enter_data({
        "column with numerator": "total_reviewed"
    })
    app.navigation.click_btn("Save & Close")
    assert app.file_upload.count_items_in_specific_status("Pending") == 1
    assert app.file_upload.count_items_in_specific_status("Complete") == 4


@pytest.mark.dependency(depends=["test_edit_quality_numerator"])
def test_edit_quality_denominator(app, login):
    app.file_upload.edit_column_connection('Quality Denominator')
    app.file_upload.check_checkbox_for_time_worked("Calculate data from cell values.")
    app.navigation.click_btn("Save & Close")
    app.verification.text_present_on_page('Field is required')

    app.file_upload.enter_data({
        "column with denominator": "label_count"
    })
    app.navigation.click_btn("Save & Close")
    assert app.file_upload.count_items_in_specific_status("Pending") == 0
    assert app.file_upload.count_items_in_specific_status("Complete") == 5
    scroll_to_page_bottom(app.driver)
    app.navigation.click_btn("Next: Project Mapping")
    time.sleep(5)


@pytest.mark.dependency(depends=["test_edit_quality_denominator"])
def test_edit_project_mapping(app, login):
    app.verification.text_present_on_page("All data is mapped! You can proceed to the next step.")
    app.navigation.click_btn("Next: User Mapping")


@pytest.mark.dependency(depends=["test_edit_project_mapping"])
def test_edit_user_mapping(app, login):
    app.verification.text_present_on_page("All data is mapped! You can proceed to the next step.")
    app.navigation.click_btn("Next: Metric Selection")


@pytest.mark.dependency(depends=["test_edit_user_mapping"])
def test_edit_metric_selection(app, login):
    app.verification.text_present_on_page("This project has no quality metrics configured or enabled. All quality data related to this project will be rejected")
    app.navigation.click_btn("Next: Preview")


@pytest.mark.dependency(depends=["test_edit_metric_selection"])
def test_preview(app, login):
    time.sleep(10)
    scroll_to_page_bottom(app.driver)
    app.navigation.click_btn("Finish and Upload Data")


@pytest.mark.dependency(depends=["test_preview"])
def test_status_of_uploaded_file(app, login):
    time.sleep(10)
    app.navigation.refresh_page()
    app.navigation.switch_to_frame("page-wrapper")
    app.file_upload.get_expected_status_of_upload_file(NEW_FILE_NAME, "Completed")
