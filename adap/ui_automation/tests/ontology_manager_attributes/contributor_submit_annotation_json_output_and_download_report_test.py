"""
1. create ontology attribute with different questions.
2. launch job
3. contributor submit annotations
4. download report and verify json output inside the report
"""
import time
from adap.ui_automation.utils.selenium_utils import *
from adap.ui_automation.services_config.annotation import create_annotation_tool_job
from adap.api_automation.services_config.builder import Builder as JobAPI
from adap.e2e_automation.services_config.job_api_support import generate_job_link
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
                                        data.ontology_attribute_json_output,
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
    # single checkbox, default not checked, not required
    app.ontology.ontology_attribute.select_question_type_from_dropdown('Checkbox')
    app.ontology.ontology_attribute.manage_single_checkbox_or_textbox_question("Checkbox", "add single checkbox")
    app.navigation.click_checkbox_by_text('Required')
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
    # pulldown menu, not required
    app.ontology.ontology_attribute.select_question_type_from_dropdown('Pulldown Menu')
    app.ontology.ontology_attribute.add_checkbox_group_or_multiple_choice_or_pulldown_menu_question("Pulldown Menu",
                                                                                                    "add pulldown menu question",
                                                                                                    "label0", "label1")
    app.navigation.click_checkbox_by_text('Required', index=-1)
    # text box, required
    app.ontology.ontology_attribute.select_question_type_from_dropdown('Text Box (Single Line)')
    app.ontology.ontology_attribute.manage_single_checkbox_or_textbox_question("Text Box (Single Line)",
                                                                               "add text box single line")
    app.navigation.click_checkbox_by_text('Required', index=-1)
    time.sleep(5)
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
def test_contributor_submit_without_annotation_ontology(app, create_shape_job):
    job_link = generate_job_link(create_shape_job, API_KEY, pytest.env)
    app.navigation.open_page(job_link)
    app.user.task.login(CONTRIBUTOR_EMAIL, CONTRIBUTOR_PASSWORD)
    app.user.close_guide()
    time.sleep(2)
    app.user.task.wait_until_job_available_for_contributor(job_link)
    app.image_annotation.submit_page()
    app.verification.text_present_on_page('This field is required.')
    assert app.verification.count_text_present_on_page('This field is required.') == 2


@pytest.mark.dependency(depends=["test_contributor_submit_without_annotation_ontology"])
def test_contributor_create_annotation_with_ontology_attributes_ontology(app, create_shape_job):
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
        assert app.verification.count_text_present_on_page('Required Field') == 2
        app.annotation.ontology_attribute_annotate.select_value_for_multiple_choice('label0')
        assert app.verification.count_text_present_on_page('Required Field') == 1
        app.annotation.ontology_attribute_annotate.input_textbox_single_line('single line')
        assert app.verification.count_text_present_on_page('Required Field') == 0
        app.annotation.ontology_attribute_annotate.save_ontology_attribute()
        app.verification.text_present_on_page('Changes saved')
        app.image_annotation.deactivate_iframe()


@pytest.mark.dependency(depends=["test_contributor_create_annotation_with_ontology_attributes_ontology"])
def test_contributor_submit_annotation_successfully_ontology(app, create_shape_job):
    app.image_annotation.submit_page()
    time.sleep(5)
    app.verification.text_present_on_page('There is no work currently available in this task.')
    app.user.task.logout()


@pytest.mark.skip(reason="TBF - https://appen.atlassian.net/browse/QED-3012")
@pytest.mark.dependency(depends=["test_contributor_submit_annotation_successfully_ontology"])
def test_download_report_ontology(app, create_shape_job):
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(create_shape_job)

    for report_type in ['Full', 'Aggregated']:
        app.job.open_tab("RESULTS")
        app.job.results.download_report(report_type, create_shape_job)
        file_name_zip = "/" + app.job.results.get_file_report_name(create_shape_job, report_type)
        full_file_name_zip = app.temp_path_file + file_name_zip

        unzip_file(full_file_name_zip)
        csv_name = str(full_file_name_zip)[:-4]

        _df = pd.read_csv(csv_name)
        assert 'annotation' in _df.columns
        assert 'image_url' in _df.columns

        random_row = random.randint(0, _df.shape[0] - 1)
        annotation_json = json.loads(_df['annotation'][random_row])
        print(annotation_json)
        if report_type == 'Full':
            assert annotation_json[0].get('class') == 'dog'
            assert 'id' in annotation_json[0]
        else:
            assert 'dog' in annotation_json[0].get('class')
            assert 'number' in annotation_json[0]
            assert 'trust' in annotation_json[0]

        assert 'coordinates' in annotation_json[0]
        assert annotation_json[0].get('type') == 'box'
        assert len(annotation_json[0].get('metadata').get('shapeAnswers')) == 5
        assert len(annotation_json[0].get('metadata').get('shapeQuestions')) == 5
        types = ['Checkbox', 'Checkbox Group', 'Multiple Choice', 'Pulldown Menu', 'Text Box (Single Line)']
        for i in range(5):
            answer = annotation_json[0].get('metadata').get('shapeAnswers')[i]
            assert answer.get('type') in types
            assert answer.get('customUserId') == ""
            assert 'name' in answer
            assert 'answer' in answer
            question = annotation_json[0].get('metadata').get('shapeQuestions')[i]
            assert question.get('type') in types
            assert question.get('customUserId') == ""
            assert 'id' in question
            assert 'data' in question

        os.remove(csv_name)
        os.remove(full_file_name_zip)


# https://appen.atlassian.net/browse/QED-2273
@pytest.mark.dependency(depends=["test_download_report_ontology"])
def test_unit_page_display_ontology_metadata_ontology(app, create_shape_job):
    CONTRIBUTOR_WORKER_ID = get_user_info('test_contributor_task')['worker_id']
    app.job.open_tab('Data')
    units = app.job.data.find_all_units_with_status('judgable')
    first_unit = units['unit id'][0]
    app.job.data.open_unit_by_id(first_unit)
    app.verification.current_url_contains("/units/%s" % first_unit)
    app.image_annotation.activate_iframe_on_unit_page()
    app.image_annotation.data_unit.find_a_judgment_dropdown_button_is_displayed()
    app.image_annotation.data_unit.click_find_a_judgment_dropdown_button()
    app.image_annotation.data_unit.click_worker_id_from_dropdown_list(CONTRIBUTOR_WORKER_ID)
    # Todo, unable to select shape at this moment