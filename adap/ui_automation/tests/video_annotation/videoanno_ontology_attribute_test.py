"""
https://appen.atlassian.net/browse/QED-2440
"""
import requests

from adap.api_automation.utils.data_util import *
from adap.data import annotation_tools_cml as data
from adap.ui_automation.services_config.annotation import create_annotation_tool_job
from adap.api_automation.services_config.builder import Builder as JobAPI, Builder
import time
from adap.e2e_automation.services_config.job_api_support import generate_job_link
from adap.ui_automation.services_config.annotation import create_peer_review_job

pytestmark = [pytest.mark.regression_video_annotation,  pytest.mark.wip_temp]

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')
DATA_FILE = get_data_file("/video_annotation/video.csv")


@pytest.fixture(scope="module")
def create_job_for_videoanno(app):
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    job_id = create_annotation_tool_job(API_KEY, DATA_FILE,
                                        data.video_annotation_object_tracking_cml,
                                        job_title="Testing ontology attribute for video annotation", units_per_page=5)
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)
    app.job.open_tab('DESIGN')
    app.navigation.click_link('Manage Video Shapes Ontology')
    ontology_file = get_data_file("/video_annotation/nested_ontology.json")
    app.ontology.upload_ontology(ontology_file)

    app.ontology.expand_nested_ontology_by_name("Nest1")
    app.ontology.expand_nested_ontology_by_name("Nest2")
    app.ontology.expand_nested_ontology_by_name("Nest3")
    app.ontology.search_class_by_name("Nest4", found=True)

    app.ontology.click_edit_class('Nest4')

    # app.navigation.click_link('Ontology Attributes')
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
        app.driver.find_element('xpath',"//label[text()='External']").click()
        app.navigation.click_link('Save')

    app.job.open_tab('LAUNCH')
    app.navigation.click_link("Launch Job")

    job = JobAPI(API_KEY, job_id=job_id)

    job.wait_until_status('running', 120)
    res = job.get_json_job_status()
    res.assert_response_status(200)
    assert 'running' == res.json_response['state'], "Job status: %s \n Expected status: %s" % (
        res.json_response['state'], "running")

    return job_id


# @allure.issue("https://appen.atlassian.net/browse/AT-5623", "BUG  on Integration  AT-5623")
@pytest.mark.dependency()
@pytest.mark.skipif(pytest.env != "integration", reason="Only integration enabled feature")
def test_submit_judgments_with_ontology_attribute(app, create_job_for_videoanno):
    job_link = generate_job_link(create_job_for_videoanno, API_KEY, pytest.env)
    app.navigation.open_page(job_link)
    app.user.close_guide()
    time.sleep(10)

    for i in range(5):
        time.sleep(10)
        app.video_annotation.activate_iframe_by_index(i)
        time.sleep(5)
        app.video_annotation.annotate_frame(mode='ontology', value={"Nest4": 1}, annotate_shape='box')
        app.verification.text_present_on_page('add single checkbox')
        app.verification.text_present_on_page('add checkbox group question')
        app.verification.text_present_on_page('add multiple choice question')
        app.verification.text_present_on_page('add pulldown menu question')
        app.verification.text_present_on_page('add text box single line')

        time.sleep(10)
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
        app.video_annotation.deactivate_iframe()

    app.video_annotation.submit_page()
    app.verification.wait_untill_text_present_on_the_page(
        text='There is no work currently available in this task.', max_time=10
    )
    app.verification.text_present_on_page('There is no work currently available in this task.')


# @allure.issue("https://appen.atlassian.net/browse/AT-5623", "BUG  on Integration  AT-5623")
@pytest.mark.skipif(pytest.env != "integration", reason="Only integration enabled feature")
@pytest.mark.dependency(depends=["test_submit_judgments_with_ontology_attribute"])
def test_download_report_for_video_annotation(app, create_job_for_videoanno):
    time.sleep(60)
    app.user.customer.open_home_page()
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(create_job_for_videoanno)
    flat_cookie_dict = {seleniumCookie['name']: seleniumCookie['value'] for seleniumCookie in
                        app.driver.get_cookies()}

    app.job.open_tab("RESULTS")

    for report_type in ['Full', 'Aggregated']:
        app.job.results.download_report(report_type, create_job_for_videoanno)
        file_name_zip = "/" + app.job.results.get_file_report_name(create_job_for_videoanno, report_type)
        full_file_name_zip = app.temp_path_file + file_name_zip

        unzip_file(full_file_name_zip)
        csv_name = str(full_file_name_zip)[:-4]

        _df = pd.read_csv(csv_name)
        assert 'video_annotation' in _df.columns
        assert 'annotation' in _df.columns
        assert 'video_url' in _df.columns

        if report_type == 'Full':
            annotation = json.loads(_df['video_annotation'][0])
            annotation_url = annotation['url']
            annotation_res = requests.get(annotation_url, cookies=flat_cookie_dict)
            assert annotation_res.status_code == 200
            assert len(annotation_res.json()['annotation']['frames']) == 25

            annotation_json_value = annotation_res.json()['annotation']['frames']['1']
            assert 'shapesInstances' in annotation_json_value
            assert 'frameRotation' in annotation_json_value
            assert 'rotatedBy' in annotation_json_value

            shape_question = annotation_json_value["shapesInstances"]
            shapesInstances = list(shape_question.values())[0]

            assert 'annotated_by' in shapesInstances
            assert 'metadata' in shapesInstances
            assert shapesInstances['metadata']['annotated_by'] == "human"
            assert len(shapesInstances['metadata']['shapeAnswers']) > 0
            assert shapesInstances['metadata']['shapeAnswers'][0]

        os.remove(csv_name)
        os.remove(full_file_name_zip)


# @allure.issue("https://appen.atlassian.net/browse/AT-5623", "BUG  on Integration  AT-5623")
@pytest.mark.dependency(depends=["test_submit_judgments_with_ontology_attribute"])
def test_video_annotation_verify_json_report(app, create_job_for_videoanno):
    time.sleep(30)
    app.job.open_tab("RESULTS")
    app.job.results.download_report('Json', create_job_for_videoanno)
    file_name_zip = "/" + app.job.results.get_file_report_name(create_job_for_videoanno, 'Json')
    full_file_name_zip = app.temp_path_file + file_name_zip

    unzip_file(full_file_name_zip)
    json_name = str(full_file_name_zip)[:-4]

    flat_cookie_dict = {seleniumCookie['name']: seleniumCookie['value'] for seleniumCookie in
                        app.driver.get_cookies()}

    api = Builder(API_KEY)
    df = pd.DataFrame(pd.read_json(json_name, lines=True), columns=['id', 'results'])

    for ind in df.index:
        unit_id = df['id'][ind]
        results = df['results'][ind]
        # check downloaded report from UI
        for jd in results['judgments']:

            annotation = json.loads(jd['data']['video_annotation'])
            assert 'type' in annotation
            assert annotation['type'] == 'video_shapes'
            assert 'valueRef' in annotation
            assert 'url' in annotation
            assert 'https://requestor-proxy.{}.cf3.us'.format(pytest.env) in annotation['url']

            annotation_res = requests.get(url=annotation['url'], cookies=flat_cookie_dict)
            assert annotation_res.status_code == 200
            json_annotation = annotation_res.json()
            assert json_annotation.get('ableToAnnotate', False)
            assert json_annotation['annotation'].get('shapes', False)
            assert json_annotation['annotation'].get('frames', False)
            assert json_annotation['annotation'].get('ontologyAttributes', False)

            assert json_annotation['annotation']['frames']['1']['frameRotation'] == 0
            assert json_annotation['annotation']['frames']['1']['rotatedBy'] == "machine"
            assert len(json_annotation['annotation']['frames']['1']['shapesInstances']) >0

        # check  report from api
        res = api.get_unit(unit_id, create_job_for_videoanno)
        assert res.status_code == 200
        assert res.json_response['id'] == unit_id

        api_judgments = res.json_response['results']['judgments']
        assert len(api_judgments) > 0

        for api_jd in api_judgments:
            annotation = json.loads(api_jd['data']['video_annotation'])
            assert 'type' in annotation
            assert annotation['type'] == 'video_shapes'
            assert 'valueRef' in annotation
            assert 'url' in annotation
            assert 'https://api-beta.{}.cf3.us/v1/redeem_token?'.format(pytest.env) in annotation['url']

            annotation_res = requests.get(url=annotation['url'])
            assert annotation_res.status_code == 200
            json_annotation = annotation_res.json()
            assert json_annotation.get('ableToAnnotate', False)
            assert json_annotation['annotation'].get('shapes', False)
            assert json_annotation['annotation'].get('frames', False)
            assert json_annotation['annotation'].get('ontologyAttributes', False)

            assert json_annotation['annotation']['frames']['1']['frameRotation'] == 0
            assert json_annotation['annotation']['frames']['1']['rotatedBy'] == "machine"
            assert len(json_annotation['annotation']['frames']['1']['shapesInstances']) > 0


# @allure.issue("https://appen.atlassian.net/browse/AT-5623", "BUG  on Integration  AT-5623")
@pytest.mark.skipif(pytest.env != "integration", reason="Only integration enabled feature")
def test_create_peerreview_for_oa(tmpdir_factory, app, create_job_for_videoanno):
    tmpdir = tmpdir_factory.mktemp('data')
    peer_review_job_id = create_peer_review_job(tmpdir, API_KEY, create_job_for_videoanno, data.video_annotation_peer_review_oa_objecttracking_cml)
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(peer_review_job_id)
    app.job.open_tab('DESIGN')
    app.navigation.click_link('Manage Video Shapes Ontology')
    ontology_file = get_data_file("/video_annotation/oa-ontology.json")
    app.ontology.upload_ontology(ontology_file)
    app.job.open_tab('LAUNCH')
    app.navigation.click_link("Launch Job")

    job = JobAPI(API_KEY, job_id=peer_review_job_id)

    job.wait_until_status('running', 120)
    res = job.get_json_job_status()
    res.assert_response_status(200)
    assert 'running' == res.json_response['state'], "Job status: %s \n Expected status: %s" % (
        res.json_response['state'], "running")

    job_link = generate_job_link(peer_review_job_id, API_KEY, pytest.env)
    app.navigation.open_page(job_link)
    app.user.close_guide()
    time.sleep(10)

    for i in range(5):
        time.sleep(10)
        app.video_annotation.activate_iframe_by_index(i)
        time.sleep(2)
        app.video_annotation.click_classes_or_objects_tab('OBJECTS')
        app.video_annotation.click_ontology_item('Nest4 1')
        time.sleep(10)
        checkbox_group = ['label0', 'label1']
        app.annotation.ontology_attribute_annotate.select_value_for_checkbox_group(checkbox_group)
        app.annotation.ontology_attribute_annotate.select_value_for_multiple_choice('label1')
        app.annotation.ontology_attribute_annotate.select_value_for_pulldown_menu()
        app.annotation.ontology_attribute_annotate.input_textbox_single_line('single line updated')
        app.annotation.ontology_attribute_annotate.save_ontology_attribute()
        app.video_annotation.deactivate_iframe()

    app.video_annotation.submit_page()
    app.verification.wait_untill_text_present_on_the_page(
        text='There is no work currently available in this task.', max_time=10
    )
    app.verification.text_present_on_page('There is no work currently available in this task.')
