import time
from adap.api_automation.utils.data_util import *
from adap.ui_automation.utils.js_utils import scroll_to_page_bottom, scroll_to_page_top

pytestmark = [pytest.mark.regression_ac_file_upload, pytest.mark.ac_ui_uat, pytest.mark.regression_ac,pytest.mark.ac_file_upload]


@pytest.fixture(scope="module", autouse=True)
def new_file_name(app):
    random_prefix = app.faker.zipcode()
    return {"file": "file_upload_{}.xlsx".format(random_prefix),
            "prefix": random_prefix}


@pytest.fixture(scope="module")
def login(app):
    USER_NAME = get_user_email('test_ui_account')
    PASSWORD = get_user_password('test_ui_account')
    app.ac_user.login_as(user_name=USER_NAME, password=PASSWORD)
    app.navigation.click_link('Partner Home')
    # app.navigation.click_link('Falcon')
    app.navigation.click_link('File Upload')
    app.navigation.click_btn('File Upload')
    app.navigation.switch_to_frame("page-wrapper")


@pytest.mark.dependency()
def test_open_file_upload_page(app, login):
    app.verification.text_present_on_page("File Upload")
    app.verification.text_present_on_page("FILE NAME")
    app.verification.text_present_on_page("DATE OF WORK")
    app.verification.text_present_on_page("PROJECTS")
    app.verification.text_present_on_page("UPLOAD TYPE")
    app.verification.text_present_on_page("CREATED AT")
    app.verification.text_present_on_page("STATUS")

# TODO filter tests
# TODO order tests
# TODO open details for file


@pytest.mark.dependency(depends=["test_open_file_upload_page"])
def test_upload_new_file_page(app, login):
    app.navigation.click_btn("Upload New File")
    app.verification.text_present_on_page("File Selection")
    #app.verification.text_present_on_page("Template")


@pytest.mark.dependency(depends=["test_upload_new_file_page"])
def test_file_selection(app, login, new_file_name, tmpdir):
    sample_file = get_data_file("/File_Upload_sample1.xlsx")

    new_sample = copy_file_with_new_name(sample_file, tmpdir, new_file_name['file'])
    assert app.file_upload.get_uploaded_files_on_selection_page() == []

    app.file_upload.enter_data({
        "Client": "Falcon",
        "Upload Type": "Productivity Data (Invoicing)",
        "Upload File": new_sample
    })

    assert app.file_upload.get_uploaded_files_on_selection_page() == [new_file_name['file']]

    app.verification.text_present_on_page("Column Connection")
    app.verification.text_present_on_page("Project Mapping")
    app.verification.text_present_on_page("User Mapping")
    app.verification.text_present_on_page("Preview")
    scroll_to_page_bottom(app.driver)
    app.navigation.click_btn('Next: Template')


@pytest.mark.dependency(depends=["test_file_selection"])
def test_template(app, login):
    app.file_upload.enter_data({
        "Templates": "SRT - Basic_Automation"
    })

    template_info = app.file_upload.get_template_preview_info()

    print(template_info)
    assert template_info[0][0] == 'Project Connection'
    assert template_info[0][1] == 'AC project: 755'
    scroll_to_page_bottom(app.driver)
    app.navigation.click_btn("Next: Column Connection")


@pytest.mark.dependency(depends=["test_template"])
def test_column_connection(app, login):
    columns = app.file_upload.get_column_connection_steps_info()
    assert columns == ['Project Connection',
                       'User Connection',
                       'Date of Work',
                       'Production Time',
                       'Units of Work Completed',
                        'Advanced Data Connection']

    app.file_upload.edit_column_connection('User Connection')
    app.verification.text_present_on_page('Edit Identifiers')
    app.verification.text_present_on_page('User Connection')
    # TODO edit column connection
    app.navigation.click_btn('Cancel')

    scroll_to_page_bottom(app.driver)
    app.navigation.click_btn("Next: Project Mapping")


@pytest.mark.dependency(depends=["test_column_connection"])
def test_project_mapping_file_upload(app, login):
    time.sleep(5)

    assert app.file_upload.get_unmapped_data() in ['0', '-']
    app.verification.text_present_on_page("All data is mapped! You can proceed to the next step.")
    app.verification.text_present_on_page("Download unmapped client data")
    app.verification.text_present_on_page("STEP 04: Project Mapping")

    scroll_to_page_bottom(app.driver)
    app.navigation.click_btn("Next: User Mapping")


@pytest.mark.dependency(depends=["test_project_mapping_file_upload"])
def test_user_mapping_file_upload(app, login):
    time.sleep(5)

    assert app.file_upload.get_unmapped_data() in ['0', '-']
    # app.verification.text_present_on_page("Proceeding with unmapped data excludes it from future reports and invoices.")
    app.verification.text_present_on_page("All data is mapped! You can proceed to the next step.")
    app.verification.text_present_on_page("Download unmapped client data")
    app.verification.text_present_on_page("STEP 05: User Mapping")

    app.navigation.click_btn("Next: Preview")


@pytest.mark.dependency(depends=["test_user_mapping_file_upload"])
def test_preview_file_upload(app, login, new_file_name):
    time.sleep(5)

    app.verification.text_present_on_page("STEP 06: Preview")
    app.verification.text_present_on_page("Review your information before uploading your data")

    assert app.file_upload.get_rows_info() =={
                "skipped_row": "0",
                "accepted_row": "4"
            }
    app.verification.text_present_on_page("Falcon")
    app.verification.text_present_on_page(new_file_name['file'])
    app.verification.text_present_on_page("Productivity Data (Invoicing)")
    app.verification.text_present_on_page("SRT - Basic_Automation")


@pytest.mark.dependency(depends=["test_preview_file_upload"])
def test_download_preview_file(app, login, new_file_name):
    time.sleep(5)
    scroll_to_page_top(app.driver)
    app.file_upload.click_button("Download Preview File")
    time.sleep(2)
    _file_name = app.temp_path_file + "/file_upload_{}-preview.csv".format(new_file_name['prefix'])
    assert file_exists(_file_name)


@pytest.mark.dependency(depends=["test_download_preview_file"])
def test_finish_uploading_file(app, login, new_file_name):
    scroll_to_page_bottom(app.driver)
    time.sleep(2)
    app.file_upload.enter_data({
        "fixedAmount": "1"
    })
    app.navigation.click_btn("Finish and Upload Data")
    time.sleep(3)
    app.file_upload.get_expected_status_of_upload_file(new_file_name['file'], "Processing")
    #print ("uploaded_files",uploaded_files)
    #assert uploaded_files[0]['file name'] == NEW_FILE_NAME
    #assert uploaded_files[0]['status'] == "Processing"


# TODO test unmapped data
