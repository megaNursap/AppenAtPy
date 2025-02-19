"""
This test covers below:
1.create image transcription job and launch it
2.submit judgments for it
3.download aggregated and full report, validate content for the report
"""
import time

import requests

from adap.api_automation.utils.data_util import *
from adap.api_automation.services_config.builder import Builder as JobAPI, Builder
from adap.e2e_automation.services_config.job_api_support import generate_job_link
from adap.ui_automation.utils.selenium_utils import find_element
from adap.data import annotation_tools_cml as data
from adap.ui_automation.services_config.annotation import create_annotation_tool_job

pytestmark = [pytest.mark.regression_image_transcription, pytest.mark.fed_ui, pytest.mark.wip_temp, pytest.mark.wip_temp_ml]

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')
DATA_FILE = get_data_file("/image_transcription/receipts.csv")


@pytest.fixture(scope="module")
def tx_job(app):
    job_id = create_annotation_tool_job(API_KEY, DATA_FILE,
                                        data.image_transcription_ocr_cml,
                                        job_title="Testing create image transcription job", units_per_page=5)

    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)

    app.job.open_tab('DESIGN')
    app.navigation.click_link('Manage Image Transcription Ontology')
    ontology_file = get_data_file("/image_transcription/ontology.json")
    app.ontology.upload_ontology(ontology_file, rebrand=True)
    app.verification.text_present_on_page("Classes Created")

    if pytest.env == 'fed':
        app.job.open_action("Settings")
        app.navigation.click_link("Select Contributor Channels")
        app.job.select_hosted_channel_by_index(save=True)

    job = JobAPI(API_KEY, job_id=job_id)
    job.launch_job()

    job.wait_until_status('running', 60)
    res = job.get_json_job_status()
    res.assert_response_status(200)
    assert 'running' == res.json_response['state'], "Job status: %s \n Expected status: %s" % (
        res.json_response['state'], "running")

    return job_id


@pytest.mark.dependency()
def test_submit_judgements_mlait(app, tx_job):
    job_link = generate_job_link(tx_job, API_KEY, pytest.env)
    app.navigation.open_page(job_link)
    app.user.close_guide()
    time.sleep(5)

    app.image_transcription.activate_iframe_by_index(4)
    app.image_transcription.full_screen()
    try:
        app.image_transcription.draw_box_with_coordination(100, 0, 30, 30)
    except Exception as r:
        app.image_transcription.draw_box_with_coordination(400, 300, 10, 10, absolute_offset=True)
    try:
        app.image_transcription.save_prediction()
    except Exception as r:
        try:
            app.image_transcription.input_transcription_text('no ocr text')
        except Exception as r:
            app.image_transcription.draw_box_with_coordination(300, 200, 10, 10, absolute_offset=True)
            app.image_transcription.input_transcription_text('no ocr text')
    app.image_transcription.full_screen()
    app.image_transcription.deactivate_iframe()
    app.image_transcription.submit_page()
    time.sleep(3)

    app.verification.text_present_on_page("Error: Annotation is empty")
    for i in range(0, 4):
        app.image_transcription.activate_iframe_by_index(i)
        app.image_transcription.full_screen()
        try:
            app.image_transcription.draw_box_with_coordination(200, 100, 50, 50)
        except Exception as r:
            app.image_transcription.draw_box_with_coordination(10, 10, 20, 20)
        time.sleep(2)
        try:
            app.image_transcription.save_prediction()
        except Exception as r:
            try:
                app.image_transcription.input_transcription_text('no ocr text')
            except Exception as r:
                app.image_transcription.draw_box_with_coordination(10, 10, 20, 20, absolute_offset=True)
                app.image_transcription.input_transcription_text('no ocr text')
        app.image_transcription.full_screen()
        app.image_transcription.deactivate_iframe()
        time.sleep(2)

    app.image_transcription.submit_page()
    time.sleep(10)
    app.verification.text_present_on_page('There is no work currently available in this task.')


@pytest.mark.dependency(depends=["test_submit_judgements_mlait"])
def test_download_reports_mlait(app_test, tx_job):
    time.sleep(60)
    app_test.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    app_test.mainMenu.jobs_page()
    app_test.job.open_job_with_id(tx_job)

    flat_cookie_dict = {seleniumCookie['name']: seleniumCookie['value'] for seleniumCookie in
                        app_test.driver.get_cookies()}

    for report_type in ['Full']:
        app_test.job.open_tab("RESULTS")
        app_test.job.results.download_report(report_type, tx_job)
        file_name_zip = "/" + app_test.job.results.get_file_report_name(tx_job, report_type)
        full_file_name_zip = app_test.temp_path_file + file_name_zip

        unzip_file(full_file_name_zip)
        csv_name = str(full_file_name_zip)[:-4]

        _df = pd.read_csv(csv_name)
        assert 'label_this' in _df.columns
        assert 'image_url' in _df.columns

        random_row = random.randint(0, _df.shape[0] - 1)
        label_this = json.loads(_df['label_this'][random_row])
        assert 'type' in label_this
        assert 'valueRef' in label_this
        assert 'url' in label_this
        assert 'urlExpiresAt' in label_this

        annotation_res = requests.get(url=label_this['url'], cookies=flat_cookie_dict)
        assert annotation_res.status_code == 200
        json_annotation = annotation_res.json()

        assert 'id' in json_annotation['annotation'][0]
        assert 'class' in json_annotation['annotation'][0]
        assert 'metadata' in json_annotation['annotation'][0]
        assert 'instance' in json_annotation['annotation'][0]
        assert 'type' in json_annotation['annotation'][0]
        assert 'coordinates' in json_annotation['annotation'][0]

        assert 'label' in json_annotation['annotation'][0]['metadata']['shapeTranscription']
        assert 'modelType' in json_annotation['annotation'][0]['metadata']['shapeTranscription']
        assert 'modelDataType' in json_annotation['annotation'][0]['metadata']['shapeTranscription']
        assert 'inputType' in json_annotation['annotation'][0]['metadata']['shapeTranscription']
        assert 'annotatedBy' in json_annotation['annotation'][0]['metadata']['shapeTranscription']
        assert 'text' in json_annotation['annotation'][0]['metadata']['shapeTranscription']
        if json_annotation['annotation'][0]['metadata']['shapeTranscription']['text'] == 'no ocr text':
            assert json_annotation['annotation'][0]['metadata']['shapeTranscription']['annotatedBy'] == 'human'
        else:
            assert json_annotation['annotation'][0]['metadata']['shapeTranscription']['annotatedBy'] == 'machine'
        assert json_annotation['annotation'][0]['metadata']['shapeTranscription']['inputType'] == 'text'

        assert 'x' in json_annotation['annotation'][0]['coordinates']
        assert 'y' in json_annotation['annotation'][0]['coordinates']
        assert 'w' in json_annotation['annotation'][0]['coordinates']
        assert 'h' in json_annotation['annotation'][0]['coordinates']

        image_url = _df['image_url'][random_row]
        image_res = requests.get(image_url)
        assert image_res.status_code == 200

        os.remove(csv_name)
        os.remove(full_file_name_zip)


@pytest.mark.dependency(depends=["test_submit_judgements_mlait"])
def test_download_json_report_mlait(app_test, tx_job):
    time.sleep(30)
    app_test.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    app_test.mainMenu.jobs_page()
    app_test.job.open_job_with_id(tx_job)

    flat_cookie_dict = {seleniumCookie['name']: seleniumCookie['value'] for seleniumCookie in
                        app_test.driver.get_cookies()}


    app_test.job.open_tab("RESULTS")
    app_test.job.results.download_report('Json', tx_job)
    file_name_zip = "/" + app_test.job.results.get_file_report_name(tx_job, 'Json')
    full_file_name_zip = app_test.temp_path_file + file_name_zip

    unzip_file(full_file_name_zip)
    json_name = str(full_file_name_zip)[:-4]

    api = Builder(API_KEY)
    df = pd.DataFrame(pd.read_json(json_name, lines=True), columns=['id', 'results'])

    for ind in df.index:
        unit_id = df['id'][ind]
        results = df['results'][ind]
        # check downloaded report from UI
        for jd in results['judgments']:
            annotation = json.loads(jd['data']['label_this'])

            assert 'type' in annotation
            assert 'valueRef' in annotation
            assert 'url' in annotation

            annotation_res = requests.get(url=annotation['url'], cookies=flat_cookie_dict)
            assert annotation_res.status_code == 200
            json_annotation = annotation_res.json()
            assert 'id' in json_annotation['annotation'][0]
            assert 'class' in json_annotation['annotation'][0]
            assert 'metadata' in json_annotation['annotation'][0]
            assert 'instance' in json_annotation['annotation'][0]
            assert 'type' in json_annotation['annotation'][0]
            assert 'coordinates' in json_annotation['annotation'][0]

            assert 'label' in json_annotation['annotation'][0]['metadata']['shapeTranscription']
            assert 'modelType' in json_annotation['annotation'][0]['metadata']['shapeTranscription']
            assert 'modelDataType' in json_annotation['annotation'][0]['metadata']['shapeTranscription']
            assert 'inputType' in json_annotation['annotation'][0]['metadata']['shapeTranscription']
            assert 'annotatedBy' in json_annotation['annotation'][0]['metadata']['shapeTranscription']
            assert 'text' in json_annotation['annotation'][0]['metadata']['shapeTranscription']
            if json_annotation['annotation'][0]['metadata']['shapeTranscription']['text'] == 'no ocr text':
                assert json_annotation['annotation'][0]['metadata']['shapeTranscription']['annotatedBy'] == 'human'
            else:
                assert json_annotation['annotation'][0]['metadata']['shapeTranscription']['annotatedBy'] == 'machine'
            assert json_annotation['annotation'][0]['metadata']['shapeTranscription']['inputType'] == 'text'

            assert 'x' in json_annotation['annotation'][0]['coordinates']
            assert 'y' in json_annotation['annotation'][0]['coordinates']
            assert 'w' in json_annotation['annotation'][0]['coordinates']
            assert 'h' in json_annotation['annotation'][0]['coordinates']

        # check  report from api
        res = api.get_unit(unit_id, tx_job)
        assert res.status_code == 200
        assert res.json_response['id'] == unit_id

        api_judgments = res.json_response['results']['judgments']
        assert len(api_judgments) > 0

        for api_jd in api_judgments:
            annotation = json.loads(api_jd['data']['label_this'])

            assert 'type' in annotation
            assert 'valueRef' in annotation
            assert 'url' in annotation
            assert 'https://api-beta.{}.cf3.us/v1/redeem_token?'.format(pytest.env) in annotation['url']

            annotation_res = requests.get(url=annotation['url'])
            assert annotation_res.status_code == 200
            json_annotation = annotation_res.json()
            assert 'id' in json_annotation['annotation'][0]
            assert 'class' in json_annotation['annotation'][0]
            assert 'metadata' in json_annotation['annotation'][0]
            assert 'instance' in json_annotation['annotation'][0]
            assert 'type' in json_annotation['annotation'][0]
            assert 'coordinates' in json_annotation['annotation'][0]

            assert 'label' in json_annotation['annotation'][0]['metadata']['shapeTranscription']
            assert 'modelType' in json_annotation['annotation'][0]['metadata']['shapeTranscription']
            assert 'modelDataType' in json_annotation['annotation'][0]['metadata']['shapeTranscription']
            assert 'inputType' in json_annotation['annotation'][0]['metadata']['shapeTranscription']
            assert 'annotatedBy' in json_annotation['annotation'][0]['metadata']['shapeTranscription']
            assert 'text' in json_annotation['annotation'][0]['metadata']['shapeTranscription']
            if json_annotation['annotation'][0]['metadata']['shapeTranscription']['text'] == 'no ocr text':
                assert json_annotation['annotation'][0]['metadata']['shapeTranscription']['annotatedBy'] == 'human'
            else:
                assert json_annotation['annotation'][0]['metadata']['shapeTranscription']['annotatedBy'] == 'machine'
            assert json_annotation['annotation'][0]['metadata']['shapeTranscription']['inputType'] == 'text'

            assert 'x' in json_annotation['annotation'][0]['coordinates']
            assert 'y' in json_annotation['annotation'][0]['coordinates']
            assert 'w' in json_annotation['annotation'][0]['coordinates']
            assert 'h' in json_annotation['annotation'][0]['coordinates']

    os.remove(json_name)
    os.remove(full_file_name_zip)