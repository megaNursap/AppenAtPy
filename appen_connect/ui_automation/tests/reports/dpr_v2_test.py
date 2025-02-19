
import datetime
import time
from faker import Faker
from adap.api_automation.utils.data_util import *
from adap.ui_automation.utils.js_utils import scroll_to_page_bottom, scroll_to_page_top

pytestmark = [pytest.mark.regression_ac_reports, pytest.mark.ac_ui_uat, pytest.mark.regression_ac, pytest.mark.ac_report]

faker = Faker()
DAY = (datetime.date.today()).day



def suffix(day):
    if 4 <= day <= 20 or 24 <= day <= 30:
        return "th"
    else:
        return ["st", "nd", "rd"][day % 10 - 1]


USER_NAME = get_user_email('test_ui_account')
PSW = get_user_password('test_ui_account')
TEMPLATE_NAME = "Template "+faker.company() + faker.zipcode()
_today = datetime.date.today()
TODAY = _today.strftime("%B %-d") + suffix(_today.day)+" " + _today.strftime("%Y")


@pytest.fixture(scope="module")
def login(app):
    app.ac_user.login_as(user_name=USER_NAME, password=PSW)
    app.navigation.click_link('Partner Home')
    app.navigation.click_link('Falcon')
    app.navigation.click_link('REPORTS')
    app.navigation.switch_to_frame("page-wrapper")
    app.verification.text_present_on_page("Daily Performance Report")


@pytest.mark.dependency()
def test_create_dpr_v2(app, login):
    # current_reports = app.dpr.get_all_reports_from_dpr_list()
    # print(current_reports)

    app.dpr.click_generate_new_report(report_type='Daily Performance Report (DPR) - v2')

    app.verification.text_present_on_page("STEP 01: DPR - V2 Report Configuration")
    app.verification.text_present_on_page("Choose Report Template")
    app.verification.text_present_on_page("Start Date")
    app.verification.text_present_on_page("End Date")
    app.verification.text_present_on_page("Template")
    app.verification.text_present_on_page("Create Report Template", is_not=False)

    scroll_to_page_top(app.driver)
    app.dpr.enter_data({"End Date": DAY})


@pytest.mark.dependency(depends=["test_create_dpr_v2"])
def test_template_details_dpr_v2(app, login):
    app.dpr.click_create_new_template()

    app.verification.text_present_on_page("Create Report Template")
    app.verification.text_present_on_page("Create new report template")
    app.verification.text_present_on_page("By starting from scratch, you are creating a new report template. Use our template builder below.")

    scroll_to_page_bottom(app.driver)
    app.navigation.click_btn("Create Report Template")

    app.verification.text_present_on_page("Report Template Details")
    app.verification.text_present_on_page("Report template name")
    app.verification.text_present_on_page("Metric formulas")
    app.verification.text_present_on_page("Copy Configuration from an Existing Report Template")


@pytest.mark.dependency(depends=["test_create_dpr_v2"])
def test_name_exists_dpr_v2(app, login):
    app.dpr.enter_data(data={
        "Report template name": 'Jobs',
        "Metric formula": "All 100%"
    })

    app.navigation.click_btn("Start")
    app.verification.text_present_on_page('This report template name already exists.')


@pytest.mark.dependency(depends=["test_name_exists_dpr_v2"])
def test_valid_name_dpr_v2(app, login):
    app.dpr.enter_data(data={
        "Report template name": TEMPLATE_NAME,
        "Metric formula": "All 100%"
    })

    app.navigation.click_btn("Start")

    app.verification.text_present_on_page("Report Template Builder")
    app.verification.text_present_on_page(TEMPLATE_NAME)
    app.verification.text_present_on_page("Project name")
    app.verification.text_present_on_page("Program name")


@pytest.mark.dependency(depends=["test_valid_name_dpr_v2"])
def test_required_fields_dpr_v2(app, login):
    scroll_to_page_bottom(app.driver)
    app.navigation.click_btn("Save & Close")
    # app.verification.text_present_on_page("Required: Select at least one market or language")
    assert app.dpr.field_is_required("Project name")
    assert app.dpr.field_is_required("Workflow name")
    # assert app.dpr.field_is_required("PROJECT ALIAS (ID)")
    # assert app.dpr.field_is_required("Market")
    # assert app.dpr.field_is_required("language")


@pytest.mark.dependency(depends=["test_required_fields_dpr_v2"])
def test_template_builder_dpr_v2(app, login):
    app.dpr.enter_data(data={
        "Project name": "Test",
        "Program name": "Test 1",
        "Workflow name": "test",
        "PROJECT ALIAS (ID)": "TEST 123",
        "Market":"UK-UA",
        "Language": "UK"
    })

    app.dpr.add_metrics("Performance", "Audit Agreement")
    app.dpr.add_metrics("Output", "Volume")

    scroll_to_page_bottom(app.driver)
    time.sleep(3)
    app.dpr.click_btn("Save & Close")

    projects_info = app.dpr.get_projects_info()
    assert projects_info == [{'name': '1Test',
                              'Program': 'Test 1',
                              'Workflows': 'test',
                              # 'Markets': 'undefined, undefined',
                              'Markets': 'UK-UA, UK',
                              'Performance': 'Audit Agreement',
                              'Output': 'Volume'}]

    app.dpr.click_create_report_template()

    app.verification.text_present_on_page(TEMPLATE_NAME)
    # TODO add more verification

    # # app.navigation.switch_to_frame("page-wrapper")
    # scroll_to_page_top(app.driver)
    # time.sleep(1)
    # print(app.driver.page_source)
    # app.dpr.enter_data({"End Date": TODAY})
    # scroll_to_page_bottom(app.driver)

    app.navigation.click_btn("Request DPR - V2 Report")

    app.navigation.refresh_page()
    app.navigation.switch_to_frame("page-wrapper")

    app.dpr.find_reports(report_type="DPR - V2")

    current_reports = app.dpr.get_all_reports_from_dpr_list()

    assert current_reports[0]['name'] == TEMPLATE_NAME
    assert current_reports[0]['type'] == 'DPR - V2'


@pytest.mark.dependency(depends=["test_template_builder_dpr_v2"])
def test_edit_report_template(app, login):
    app.dpr.click_generate_new_report(report_type='Daily Performance Report (DPR) - v2')

    time.sleep(2)
    app.dpr.choose_report_template(TEMPLATE_NAME)

    app.dpr.click_btn("Edit program")
    projects_info = app.dpr.get_projects_info()
    assert projects_info == [{'name': '1Test',
                              'Program': 'Test 1',
                              'Workflows': 'test',
                              'Markets': 'UK-UA, UK',
                              'Performance': 'Audit Agreement',
                              'Output': 'Volume'}]

    app.dpr.click_edit_program("Test")

    app.dpr.enter_data(data={
        "Project name": "Test Updated",
        "Program name": "Test 1 Updated",
        "Workflow name": "test updated"
    })

    app.dpr.add_metrics("Performance", "Agreement")
    app.dpr.add_metrics("Output", "Production Hours")
    scroll_to_page_bottom(app.driver)
    app.dpr.click_btn("Save & Close")

    projects_info = app.dpr.get_projects_info()
    assert projects_info == [{'name': '1Test Updated',
                              'Program': 'Test 1 Updated',
                              'Workflows': 'test updated',
                              'Markets': 'UK-UA, UK',
                              'Performance': 'Audit Agreement, Agreement',
                              'Output': 'Volume, Production Hours'}]

    app.dpr.click_create_report_template()

    app.verification.text_present_on_page('Test 1 Updated')
    app.verification.text_present_on_page('test updated')
    app.verification.text_present_on_page('Production Hours')
