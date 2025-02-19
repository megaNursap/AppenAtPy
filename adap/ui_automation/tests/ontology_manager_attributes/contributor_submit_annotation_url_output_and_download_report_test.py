"""
https://appen.atlassian.net/browse/QED-1983
https://appen.atlassian.net/browse/QED-1984
1. create ontology attribute with different questions.
2. launch job
3. contributor submit annotations
4. download report and verify url output inside the report
"""
import time
from adap.ui_automation.utils.selenium_utils import *
from adap.ui_automation.services_config.annotation import create_annotation_tool_job
from adap.api_automation.services_config.builder import Builder as JobAPI
from adap.e2e_automation.services_config.job_api_support import generate_job_link
from selenium.webdriver.common.keys import Keys
from adap.api_automation.utils.data_util import *
from adap.data import annotation_tools_cml as data


pytestmark = [pytest.mark.regression_ontology_attribute, pytest.mark.fed_ui]

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')
DATA_FILE = get_data_file("/image_annotation/catdog.csv")
CONTRIBUTOR_EMAIL = get_user_email('test_contributor_task')
CONTRIBUTOR_PASSWORD = get_user_password('test_contributor_task')


@pytest.fixture(scope="module")
def create_shape_job(app):
    job_id = create_annotation_tool_job(API_KEY, DATA_FILE,
                                        data.ontology_attribute_url_output,
                                        job_title="Testing ontology attribute from contributor", units_per_page=2)
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)

    app.job.open_tab('DESIGN')
    app.navigation.click_link('Manage Image Annotation Ontology')

    ontology_file = get_data_file("/image_annotation/ontology.json")
    app.ontology.upload_ontology(ontology_file)
    app.verification.text_present_on_page("Classes Created")

    app.ontology.click_edit_class('dog')
    app.ontology.ontology_attribute.click_edit_ontology_attribute()
    # single checkbox, default checked, required
    app.ontology.ontology_attribute.select_question_type_from_dropdown('Checkbox')
    app.ontology.ontology_attribute.manage_single_checkbox_or_textbox_question("Checkbox", "add single checkbox")
    app.navigation.click_checkbox_by_text('Defaults checked?')
    # checkbox group, required
    app.ontology.ontology_attribute.select_question_type_from_dropdown('Checkbox Group')
    app.ontology.ontology_attribute.add_checkbox_group_or_multiple_choice_or_pulldown_menu_question("Checkbox Group",
                                                                                                    "add checkbox group question",
                                                                                                    "label0", "label1")
    app.ontology.ontology_attribute.add_tips_and_hints_in_additional_options("Checkbox Group", "hints", "result_header")
    # multiple choice, required
    app.ontology.ontology_attribute.select_question_type_from_dropdown('Multiple Choice')
    app.ontology.ontology_attribute.add_checkbox_group_or_multiple_choice_or_pulldown_menu_question("Multiple Choice",
                                                                                                    "add multiple choice question",
                                                                                                    "label0", "label1")
    # pulldown menu, required
    app.ontology.ontology_attribute.select_question_type_from_dropdown('Pulldown Menu')
    app.ontology.ontology_attribute.add_checkbox_group_or_multiple_choice_or_pulldown_menu_question("Pulldown Menu",
                                                                                                    "add pulldown menu question",
                                                                                                    "label0", "label1")
    # text box, required
    app.ontology.ontology_attribute.select_question_type_from_dropdown('Text Box (Single Line)')
    app.ontology.ontology_attribute.manage_single_checkbox_or_textbox_question("Text Box (Single Line)",
                                                                               "add text box single line")
    app.navigation.click_checkbox_by_text('Required', index=-1)
    app.navigation.click_btn('Done')
    app.navigation.click_btn('Save')

    # launch job
    app.job.open_action("Settings")
    if pytest.env == 'fed':
        app.navigation.click_link("Select Contributor Channels")
        app.job.select_hosted_channel_by_index(save=True)
    else:
        app.driver.find_element('xpath',"//label[@for='externalChannelsEnabled' or text()='External']").click()
        app.navigation.click_link('Save')

    app.job.open_tab('LAUNCH')
    app.navigation.click_link("Launch Job")

    job = JobAPI(API_KEY, job_id=job_id)

    job.wait_until_status('running', 120)
    res = job.get_json_job_status()
    res.assert_response_status(200)
    assert 'running' == res.json_response['state'], "Job status: %s \n Expected status: %s" % (
        res.json_response['state'], "running")
    app.user.logout()

    return job_id


@pytest.mark.dependency()
def test_contributor_submit_without_annotation(app, create_shape_job):
    job_link = generate_job_link(create_shape_job, API_KEY, pytest.env)
    app.navigation.open_page(job_link)
    app.user.task.login(CONTRIBUTOR_EMAIL, CONTRIBUTOR_PASSWORD)
    app.user.close_guide()
    time.sleep(2)
    app.user.task.wait_until_job_available_for_contributor(job_link)
    app.image_annotation.submit_page()
    # seems dev in change of error message, disable it firstly.
    # app.verification.text_present_on_page('This field is required.')
    # assert app.verification.count_text_present_on_page('This field is required.') == 2


@pytest.mark.dependency(depends=["test_contributor_submit_without_annotation"])
def test_contributor_create_annotation_with_ontology_attributes(app, create_shape_job):
    for i in range(2):
        app.image_annotation.activate_iframe_by_index(i)
        app.image_annotation.annotate_with_ontology_attribute(mode='ontology', value={"dog": 1}, max_annotate=5)
        app.verification.text_present_on_page('add single checkbox')
        app.verification.text_present_on_page('add checkbox group question')
        app.verification.text_present_on_page('add multiple choice question')
        app.verification.text_present_on_page('add pulldown menu question')
        app.verification.text_present_on_page('add text box single line')

        checkbox_group = ['label0', 'label1']
        app.annotation.ontology_attribute_annotate.select_value_for_checkbox_group(checkbox_group)
        app.annotation.ontology_attribute_annotate.save_ontology_attribute()
        app.verification.text_present_on_page('Required Field')
        assert app.verification.count_text_present_on_page('Required Field') == 3
        app.annotation.ontology_attribute_annotate.select_value_for_multiple_choice('label0')
        assert app.verification.count_text_present_on_page('Required Field') == 2
        app.annotation.ontology_attribute_annotate.select_value_for_pulldown_menu()
        assert app.verification.count_text_present_on_page('Required Field') == 1
        app.annotation.ontology_attribute_annotate.input_textbox_single_line('single line')
        assert app.verification.count_text_present_on_page('Required Field') == 0
        app.annotation.ontology_attribute_annotate.save_ontology_attribute()
        app.verification.text_present_on_page('Changes saved')
        if i == 0:
            app.image_annotation.deactivate_iframe()


@pytest.mark.dependency(depends=["test_contributor_create_annotation_with_ontology_attributes"])
def test_contributor_copy_paste_delete_annotation(app, create_shape_job):
    app.image_annotation.combine_hotkey(Keys.COMMAND, 'c')
    app.image_annotation.combine_hotkey(Keys.COMMAND, 'v')
    app.image_annotation.single_hotkey(Keys.DELETE)
    app.image_annotation.deactivate_iframe()


@pytest.mark.dependency(depends=["test_contributor_copy_paste_delete_annotation"])
def test_contributor_submit_annotation_successfully(app, create_shape_job):
    app.image_annotation.submit_page()
    time.sleep(5)
    app.verification.text_present_on_page('There is no work currently available in this task.')


@pytest.mark.dependency(depends=["test_contributor_submit_annotation_successfully"])
def test_download_report_ontology_annotation(app_test, create_shape_job):

    app_test.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    app_test.mainMenu.jobs_page()
    app_test.job.open_job_with_id(create_shape_job)

    for report_type in ['Full', 'Aggregated']:
        app_test.job.open_tab("RESULTS")
        app_test.job.results.download_report(report_type, create_shape_job)
        file_name_zip = "/" + app_test.job.results.get_file_report_name(create_shape_job, report_type)
        full_file_name_zip = app_test.temp_path_file + file_name_zip

        unzip_file(full_file_name_zip)
        csv_name = str(full_file_name_zip)[:-4]

        _df = pd.read_csv(csv_name)
        assert 'annotation' in _df.columns
        assert 'image_url' in _df.columns
        # Report url feature changed, need update later
        # if report_type == 'Full':
        #     random_row = random.randint(0, _df.shape[0] - 1)
        #     annotation_url = json.loads(_df['annotation'][random_row]).get('url')
        #     import requests
        #     annotation_res = requests.get(annotation_url)
        #     assert annotation_res.status_code == 200
        #     assert annotation_res.json().get("ableToAnnotate")
        #     assert 'id' in annotation_res.json().get("annotation")[0]
        #     assert 'coordinates' in annotation_res.json().get("annotation")[0]
        #     assert annotation_res.json().get("annotation")[0].get('class') == 'dog'
        #     assert annotation_res.json().get("annotation")[0].get('type') == 'box'
        #     assert len(annotation_res.json().get("annotation")[0].get('metadata').get('shapeAnswers')) == 5
        #     assert len(annotation_res.json().get("annotation")[0].get('metadata').get('shapeQuestions')) == 5
        #     types = ['Checkbox', 'Checkbox Group', 'Multiple Choice', 'Pulldown Menu', 'Text Box (Single Line)']
        #     for i in range(5):
        #         answer = annotation_res.json().get("annotation")[0].get('metadata').get('shapeAnswers')[i]
        #         assert answer.get('type') in types
        #         assert answer.get('customUserId') == ""
        #         assert 'name' in answer
        #         assert 'answer' in answer
        #         question = annotation_res.json().get("annotation")[0].get('metadata').get('shapeQuestions')[i]
        #         assert question.get('type') in types
        #         assert question.get('customUserId') == ""
        #         assert 'id' in question
        #         assert 'data' in question

        # app_test.navigation.click_link("Force regenerate this report")
        # progressbar = find_element(app_test.driver, "//div[@id='progressbar']")
        # time_to_wait = 30
        # current_time = 0
        # while current_time < time_to_wait:
        #     progress = progressbar.get_attribute('aria-valuenow')
        #     if progress == '100':
        #         break
        #     else:
        #         current_time += 1
        #         time.sleep(1)
        # else:
        #     msg = f'Max wait time reached, regenerate report failed'
        #     raise Exception(msg)

        os.remove(csv_name)
        os.remove(full_file_name_zip)