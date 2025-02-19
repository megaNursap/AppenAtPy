"""
QED-2153  https://appen.atlassian.net/browse/QED-2153
[AC] File Upload: Time Worked Calculation
"""

import time
from adap.api_automation.utils.data_util import *
from adap.ui_automation.utils.js_utils import scroll_to_page_bottom

pytestmark = [pytest.mark.regression_ac_file_upload, pytest.mark.regression_ac,pytest.mark.ac_file_upload]

USER_NAME = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
faker = Faker()
random_prefix = faker.zipcode()

NEW_FILE_NAME = "file_upload_worked_time_{}.xlsx".format(random_prefix)
TEMPLATE_NAME = "falcon_template_time" + random_prefix


@pytest.fixture(scope="module")
def login_set_up_file_upload(app, tmpdir_factory):
    app.ac_user.login_as(user_name=USER_NAME, password=PASSWORD)
    app.navigation.click_link('Partner Home')
    # app.navigation.click_link('Falcon')
    app.navigation.click_link('File Upload')
    app.navigation.click_btn('File Upload')

    app.navigation.switch_to_frame("page-wrapper")
    app.navigation.click_btn("Upload New File")

    sample_file = get_data_file("/upload_file_worked_time.xlsx")

    new_sample = copy_file_with_new_name(sample_file, tmpdir_factory.mktemp("data"), NEW_FILE_NAME)
    assert app.file_upload.get_uploaded_files_on_selection_page() == []

    app.file_upload.enter_data({
        "Client": "Falcon",
        "Upload Type": "Productivity Data (Invoicing)",
        "Upload File": new_sample
    })

    scroll_to_page_bottom(app.driver)
    app.navigation.click_btn('Next: Template')

    app.file_upload.open_toggle('CREATE NEW TEMPLATE')

    app.file_upload.enter_data({
        "Template name": TEMPLATE_NAME,
        "Timezone": "US/Pacific"
    })
    app.navigation.click_btn("Next: Column Connection")

    time.sleep(10)

    app.verification.text_present_on_page('Project Connection')
    app.verification.text_present_on_page('User Connection')
    app.verification.text_present_on_page('Date of Work')
    app.verification.text_present_on_page('Production Time')

    app.file_upload.edit_column_connection('Production Time')
    app.file_upload.check_checkbox_for_time_worked("Calculate data from cell values, using")


def test_upload_time_worked_init_hours(app,login_set_up_file_upload):
    app.file_upload.enter_data({
        "column with Production Time": "total_review_time",
        "time unit": "Hour"
    })

    app.navigation.click_btn('Calculate Production Time')
    # TODO last row excluded because of bug https://appen.atlassian.net/browse/ACE-9583
    for row in app.file_upload.get_time_worked_table()[:-1]:
        assert row['TOTAL_REVIEW_TIME'] == row['TIME WORKED (HOURS)']


@pytest.mark.parametrize('multiply, round_num',
                          [(2, None),
                           (3, 1),
                           (-1, 1),
                           (-10, 1)
                           ])
def test_upload_multiply_time_worked(app,login_set_up_file_upload, multiply, round_num):

    app.file_upload.enter_data({
        "multiply by": multiply,
        "round number": round_num
    })

    app.navigation.click_btn('Calculate Production Time')
    for row in app.file_upload.get_time_worked_table()[:-1]:
        total_time = float(row['TOTAL_REVIEW_TIME'])
        if round_num:
            calculated_time = float(row['TIME WORKED (HOURS)'])
            assert round(total_time*multiply, round_num-1) == calculated_time
        else:
            calculated_time = float(row['TIME WORKED (HOURS)'])
            assert total_time * multiply == calculated_time

    # tear down
    app.file_upload.enter_data({
        "multiply by": 1,
        "round number": 'None'
    })


@pytest.mark.parametrize('time_unit, rate',
                         [('Millisecond', 3600000),
                          ('Second', 3600),
                          ('Minute', 60),
                          ('Hour', 1)
                          ])
def test_upload_time_unit_time_worked(app, login_set_up_file_upload, time_unit, rate):

    app.file_upload.enter_data({
        "time unit": time_unit
    })

    app.navigation.click_btn('Calculate Production Time')

    for row in app.file_upload.get_time_worked_table()[:-1]:
        total_time = float(row['TOTAL_REVIEW_TIME'])
        calculated_time = float(row['TIME WORKED (HOURS)'])
        assert round(total_time/rate, 3)  == round(calculated_time, 3)


# TODO 'Second' is nit working - bug
# https://appen.atlassian.net/browse/ACE-9598
@pytest.mark.parametrize('time_unit, round_num, rate',
                         [('Hour', 1, 0),
                          ('Hour', 0.001, 3),
                          ('Hour', 0.01, 2),
                          ('Hour', 10, -1),
                          ('Hour', 100, -2)
                          # ('Second', 0.01, 2),
                          # ('Second', 0.001, 3),
                          # ('Second', 1, 0)
                          ])
def test_upload_round_time_worked(app, login_set_up_file_upload, time_unit, round_num, rate):
    app.file_upload.enter_data({
        "time unit": time_unit,
        "round number": round_num
    })

    app.navigation.click_btn('Calculate Production Time')

    for row in app.file_upload.get_time_worked_table()[:-1]:
        total_time = float(row['TOTAL_REVIEW_TIME'])
        if round_num <= 1:
            calculated_time = float(row['TIME WORKED (HOURS)'])
            assert round(total_time, rate) == calculated_time
        else:
            calculated_time = int(row['TIME WORKED (HOURS)'])
            assert int(round(total_time, rate)) == calculated_time
