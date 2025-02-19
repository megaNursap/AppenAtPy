"""
This test covers a simple end to end flow including below items:
1. create job via cml
2. select host channel if it is fed env.
3. launch the job
4. do judgments via internal link
5. download full and aggregate report
"""

import requests

from adap.api_automation.utils.data_util import *
from adap.api_automation.services_config.builder import Builder as JobAPI, Builder
from adap.e2e_automation.services_config.job_api_support import generate_job_link
from adap.ui_automation.utils.selenium_utils import *
from adap.data import annotation_tools_cml as data
from adap.ui_automation.services_config.annotation import create_annotation_tool_job

pytestmark = [pytest.mark.regression_image_annotation, pytest.mark.fed_ui, pytest.mark.wip_temp]

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')
DATA_FILE = get_data_file("/image_annotation/catdog.csv")


@pytest.fixture(scope="module")
def im_anno_job(app):
    job_id = create_annotation_tool_job(API_KEY, DATA_FILE,
                                        data.image_annotation__report_url_cml,
                                        job_title="Testing create image annotation job", units_per_page=2)
    # job_id = 1776997
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)

    app.job.open_tab('DESIGN')
    app.navigation.click_link('Manage Image Annotation Ontology')

    ontology_file = get_data_file("/image_annotation/ontology.json")
    app.ontology.upload_ontology(ontology_file, rebrand=True)
    app.verification.text_present_on_page("Classes Created")
    time.sleep(3)
    # need to select hosted channel if it is fed env
    if pytest.env == 'fed':
        app.job.open_action("Settings")
        app.navigation.click_link("Select Contributor Channels")
        app.job.select_hosted_channel_by_index(save=True)

    job = JobAPI(API_KEY, job_id=job_id)
    job.launch_job()

    job.wait_until_status('running', 120)
    res = job.get_json_job_status()
    res.assert_response_status(200)
    assert 'running' == res.json_response['state'], "Job status: %s \n Expected status: %s" % (
        res.json_response['state'], "running")

    return job_id


@pytest.mark.dependency()
def test_submit_judgements_image_annotation(app, im_anno_job):
    job_link = generate_job_link(im_anno_job, API_KEY, pytest.env)
    app.navigation.open_page(job_link)
    app.user.close_guide()
    time.sleep(5)

    app.image_annotation.activate_iframe_by_index(0)
    app.image_annotation.annotate_image(mode='ontology', value={"cat": 3})
    app.image_annotation.deactivate_iframe()
    app.image_annotation.submit_page()

    assert app.verification.wait_untill_text_present_on_the_page(text="Error: Annotation is empty", max_time=10)

    app.image_annotation.activate_iframe_by_index(1)
    app.image_annotation.annotate_image(mode='ontology', value={"dog": 2})
    app.image_annotation.deactivate_iframe()
    app.image_annotation.submit_page()

    app.verification.wait_untill_text_present_on_the_page(
        text="There is no work currently available in this task.", max_time=10
    )
    app.verification.text_present_on_page('There is no work currently available in this task.')


@pytest.mark.dependency(depends=["test_submit_judgements_image_annotation"])
def test_download_reports_image_annotation(app, im_anno_job):
    app.user.customer.open_home_page()
    login = app.driver.find_elements('xpath',"//input[@type='email']")
    if len(login) > 0:
        app.user.customer.login(user_name=USER_EMAIL, password=PASSWORD)

    app.mainMenu.jobs_page()
    app.job.open_job_with_id(im_anno_job)
    # https://appen.atlassian.net/browse/AT-4413
    # for report_type in ['Full', 'Aggregated']:
    for report_type in ['Full']:
        app.job.open_tab("RESULTS")
        app.job.results.download_report(report_type, im_anno_job)
        file_name_zip = "/" + app.job.results.get_file_report_name(im_anno_job, report_type)
        full_file_name_zip = app.temp_path_file + file_name_zip

        unzip_file(full_file_name_zip)
        csv_name = str(full_file_name_zip)[:-4]

        _df = pd.read_csv(csv_name)
        assert 'annotation' in _df.columns
        assert 'image_url' in _df.columns
        os.remove(csv_name)
        os.remove(full_file_name_zip)


@pytest.mark.dependency(depends=["test_download_reports_image_annotation"])
def test_image_annotation_verify_json_report(app, im_anno_job):
    time.sleep(30)
    app.job.open_tab("RESULTS")
    app.job.results.download_report('Json', im_anno_job)
    file_name_zip = "/" + app.job.results.get_file_report_name(im_anno_job, 'Json')
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

            annotation = json.loads(jd['data']['annotation'])

            assert 'type' in annotation
            assert 'valueRef' in annotation
            assert 'url' in annotation

            annotation_res = requests.get(url=annotation['url'], cookies=flat_cookie_dict)
            assert annotation_res.status_code == 200
            json_annotation = annotation_res.json()
            assert json_annotation.get('annotation', False)
            assert json_annotation['annotation'][0].get('coordinates', False)
            assert json_annotation['annotation'][0].get('id', False)
            assert json_annotation['annotation'][0].get('class') in ['cat', 'dog']
            assert json_annotation['annotation'][0].get('type') == 'box'

        # check  report from api
        res = api.get_unit(unit_id, im_anno_job)
        assert res.status_code == 200
        assert res.json_response['id'] == unit_id

        api_judgments = res.json_response['results']['judgments']
        assert len(api_judgments) > 0

        for api_jd in api_judgments:
            annotation = json.loads(api_jd['data']['annotation'])
            assert 'type' in annotation
            assert 'valueRef' in annotation
            assert 'url' in annotation

            assert 'https://api-beta.{}.cf3.us/v1/redeem_token?'.format(pytest.env) in annotation['url']

            annotation_res = requests.get(url=annotation['url'])
            assert annotation_res.status_code == 200
            json_annotation = annotation_res.json()
            assert json_annotation.get('annotation', False)
            assert json_annotation['annotation'][0].get('coordinates', False)
            assert json_annotation['annotation'][0].get('id', False)
            assert json_annotation['annotation'][0].get('class') in ['cat', 'dog']
            assert json_annotation['annotation'][0].get('type') == 'box'


def test_image_annotation_without_judgments(app):
    "Validate report and logs for submitted shape job without judgments"

    job_id = create_annotation_tool_job(API_KEY, DATA_FILE,
                                        data.image_annotation_only_if_cml,
                                        job_title="Testing image annotation job with no judgments", units_per_page=2)

    # Commented out the below line out because the user was already logged in and failed to find the username and password elements
    # app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)
    job_page_url = app.driver.current_url

    job = JobAPI(API_KEY, job_id=job_id)
    job.launch_job()

    job.wait_until_status('running', 120)
    res = job.get_json_job_status()
    res.assert_response_status(200)

    job_link = generate_job_link(job_id, API_KEY, pytest.env)
    app.navigation.open_page(job_link)
    app.user.close_guide()
    time.sleep(5)

    app.job.judgements.create_random_judgments_answer()

    app.navigation.open_page(job_page_url)
    app.job.open_tab("RESULTS")

    app.job.results.download_report("Full", job_id)

    file_name_zip = "/" + app.job.results.get_file_report_name(job_id, "Full")
    full_file_name_zip = app.temp_path_file + file_name_zip
    assert file_exists(full_file_name_zip)

    unzip_file(full_file_name_zip)
    csv_name = str(full_file_name_zip)[:-4]

    _df = pd.read_csv(csv_name)
    assert 'sample_radio_buttons' in _df.columns

    col_value = _df['sample_radio_buttons'].tolist()
    assert len(col_value) == 2