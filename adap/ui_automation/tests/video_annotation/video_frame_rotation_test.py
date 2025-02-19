"""
https://appen.atlassian.net/browse/QED-2110
https://appen.atlassian.net/browse/QED-2239
This test covers a simple end to end flow for video annotation frame rotation feature:
1. create video annotation job enables frame rotation via cml
2. select host channel if it is fed env.
3. launch the job
4. check hot keys to rotate the frame in preview mode
5. check rotation interpolation
5. contributor check frame rotation feature and submit judgments
6. download full and aggregate report
7. leverage above full report to create peer review job. check negative scenario where data has rotation but cml does not have the tag
8. update cml to include the rotation tag and check peer review job for positive case
"""
from adap.api_automation.utils.data_util import *
from adap.ui_automation.services_config.video_annotation import create_video_annotation_job
import time
import json
from adap.data import annotation_tools_cml as data
from adap.e2e_automation.services_config.job_api_support import generate_job_link
from adap.ui_automation.services_config.annotation import create_peer_review_job
from selenium.webdriver.common.keys import Keys
from adap.api_automation.services_config.builder import Builder


pytestmark = [pytest.mark.regression_video_annotation]

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')
DATA_FILE = get_data_file("/video_annotation/video_withoutannotation.csv")
CONTRIBUTOR_EMAIL = get_user_email('test_contributor_task')
CONTRIBUTOR_PASSWORD = get_user_password('test_contributor_task')
WORKER_ID = get_user_worker_id('test_contributor_task')


@pytest.fixture(scope="module")
def frame_rotation_job(app):
    job_id = create_video_annotation_job(app, API_KEY, data.video_annotation_frame_rotation_cml, USER_EMAIL,
                                         PASSWORD, DATA_FILE)
    return job_id


@pytest.mark.dependency()
def test_frame_rotation_hotkeys_and_rotation_interpolation(app, frame_rotation_job):
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(frame_rotation_job)
    job_window = app.driver.window_handles[0]
    app.job.preview_job()
    time.sleep(5)
    app.video_annotation.activate_iframe_by_index(0)
    time.sleep(5)
    # try hotkey https://appen.atlassian.net/browse/AT-2779
    # frame 1--0° by default, go to frame 5 to make it rotate to around 183°
    for i in range(0, 4):
        app.video_annotation.next_frame()
    app.video_annotation.click_image_rotation_button()
    app.video_annotation.image_rotation_slider_bar_available()
    assert app.video_annotation.get_image_rotation_degree() == "0°"
    app.video_annotation.move_image_rotation_knob()
    degree = int(app.video_annotation.get_image_rotation_degree()[:-1])
    app.video_annotation.combine_hotkey(Keys.COMMAND, ",")
    left_one_degree = int(app.video_annotation.get_image_rotation_degree()[:-1])
    assert left_one_degree == degree - 1
    app.video_annotation.combine_hotkey(Keys.COMMAND, ".")
    right_one_degree = int(app.video_annotation.get_image_rotation_degree()[:-1])
    assert right_one_degree == left_one_degree + 1
    app.video_annotation.combine_hotkey([Keys.COMMAND, Keys.SHIFT], ",")
    left_fifteen_degree = int(app.video_annotation.get_image_rotation_degree()[:-1])
    assert left_fifteen_degree == right_one_degree - 15
    app.video_annotation.combine_hotkey([Keys.COMMAND, Keys.SHIFT], ".")
    right_fifteen_degree = int(app.video_annotation.get_image_rotation_degree()[:-1])
    assert right_fifteen_degree == left_fifteen_degree + 15
    app.video_annotation.combine_hotkey(Keys.COMMAND, "z")
    undo_degree = int(app.video_annotation.get_image_rotation_degree()[:-1])
    assert undo_degree == left_fifteen_degree
    app.video_annotation.combine_hotkey(Keys.COMMAND, "y")
    redo_degree = int(app.video_annotation.get_image_rotation_degree()[:-1])
    assert redo_degree == right_fifteen_degree

    # try rotation interpolation https://appen.atlassian.net/browse/AT-3452
    # check frame 6, verify it has same degree as frame 5
    app.video_annotation.next_frame()
    frame6_degree = int(app.video_annotation.get_image_rotation_degree()[:-1])
    assert frame6_degree == degree
    # check frame 4 degree
    app.video_annotation.previous_frame()
    app.video_annotation.previous_frame()
    assert int(app.video_annotation.get_image_rotation_degree()[:-1]) in range(int(degree*3/4)-5, int(degree*3/4)+5)
    # check frame 3 degree
    app.video_annotation.previous_frame()
    assert int(app.video_annotation.get_image_rotation_degree()[:-1]) in range(int(degree/2)-5, int(degree/2)+5)
    # check frame 2 degree
    app.video_annotation.previous_frame()
    assert int(app.video_annotation.get_image_rotation_degree()[:-1]) in range(int(degree*1/4)-5, int(degree*1/4)+5)
    # check frame 1 degree
    app.video_annotation.previous_frame()
    assert int(app.video_annotation.get_image_rotation_degree()[:-1]) == 0
    # rotate frame 1 to 183°
    app.video_annotation.move_image_rotation_knob()
    assert int(app.video_annotation.get_image_rotation_degree()[:-1]) == degree
    # check frame 2 again
    app.video_annotation.next_frame()
    assert int(app.video_annotation.get_image_rotation_degree()[:-1]) == degree
    # check frame 3 again
    app.video_annotation.next_frame()
    assert int(app.video_annotation.get_image_rotation_degree()[:-1]) == degree
    # check frame 4 again
    app.video_annotation.next_frame()
    assert int(app.video_annotation.get_image_rotation_degree()[:-1]) == degree
    # check frame 5 again
    app.video_annotation.next_frame()
    assert int(app.video_annotation.get_image_rotation_degree()[:-1]) == degree
    app.image_transcription.deactivate_iframe()
    app.driver.close()
    app.navigation.switch_to_window(job_window)
    app.user.logout()


@pytest.mark.dependency(depends=["test_frame_rotation_hotkeys_and_rotation_interpolation"])
def test_frame_rotation_submit_judgments(app, frame_rotation_job):
    job_link = generate_job_link(frame_rotation_job, API_KEY, pytest.env)
    app.navigation.open_page(job_link)
    app.user.task.login(CONTRIBUTOR_EMAIL, CONTRIBUTOR_PASSWORD)
    app.user.close_guide()
    time.sleep(2)
    app.user.task.wait_until_job_available_for_contributor(job_link)
    for i in range(0, 5):
        app.video_annotation.activate_iframe_by_index(i)
        time.sleep(5)
        app.video_annotation.draw_box_with_box_params()
        app.video_annotation.combine_hotkey([Keys.COMMAND, Keys.SHIFT], ">")
        app.video_annotation.image_rotation_slider_bar_available()
        assert app.video_annotation.get_image_rotation_degree() == "15°"
        app.video_annotation.deactivate_iframe()
        time.sleep(2)

    app.video_annotation.submit_page()
    time.sleep(5)
    app.user.task.logout()

    assert app.verification.text_present_on_page('Login')


@pytest.mark.dependency(depends=["test_frame_rotation_submit_judgments"])
def test_frame_rotation_download_reports(app, frame_rotation_job):
    time.sleep(120)
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(frame_rotation_job)

    for report_type in ['Full', 'Aggregated']:
        app.job.open_tab("RESULTS")
        app.job.results.download_report(report_type, frame_rotation_job)
        file_name_zip = "/" + app.job.results.get_file_report_name(frame_rotation_job, report_type)
        full_file_name_zip = app.temp_path_file + file_name_zip

        unzip_file(full_file_name_zip)
        csv_name = str(full_file_name_zip)[:-4]

        _df = pd.read_csv(csv_name)
        assert 'video_annotation' in _df.columns
        assert 'video_url' in _df.columns

        random_row = random.randint(0, _df.shape[0] - 1)
        video_annotation_data = _df['video_url'][random_row]
        # annotation_url = json.loads(video_annotation_data)
        import requests
        annotation_res = requests.get(video_annotation_data)
        assert annotation_res.status_code == 200


@pytest.mark.dependency(depends=["test_frame_rotation_download_reports"])
def test_frame_rotation_peer_review_job(tmpdir_factory, app, frame_rotation_job):
    tmpdir = tmpdir_factory.mktemp('data')
    job_id = create_peer_review_job(tmpdir, API_KEY, frame_rotation_job, data.video_annotation_peer_review_cml)
    app.user.customer.open_home_page()
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)
    app.job.open_tab('DESIGN')
    app.driver.refresh()
    app.navigation.click_link('Manage Video Shapes Ontology')
    ontology_file = get_data_file("/video_annotation/ontology.json")
    app.ontology.upload_ontology(ontology_file)
    # app.verification.text_present_on_page("2/1000 Classes Created")
    time.sleep(3)

    job = Builder(API_KEY, job_id=job_id)
    job.launch_job()
    job.wait_until_status('running', 120)
    res = job.get_json_job_status()
    res.assert_response_status(200)
    assert 'running' == res.json_response['state'], "Job status: %s \n Expected status: %s" % (
        res.json_response['state'], "running")

    app.job.preview_job()
    time.sleep(8)
    # https://appen.atlassian.net/browse/AT-3463
    app.video_annotation.activate_iframe_by_index(0)
    app.video_annotation.deactivate_iframe()
    # update cml and check regular peer review job
    updated_payload = {
        'key': API_KEY,
        'job': {
            'cml': data.video_annotation_frame_rotation_peer_review_cml
        }
    }
    job.update_job(payload=updated_payload)

    app.navigation.refresh_page()
    app.video_annotation.activate_iframe_by_index(0)
    app.verification.text_present_on_page('Question Unavailable', is_not=False)
    app.verification.text_present_on_page('Frame rotation is required', is_not=False)
    app.video_annotation.click_image_rotation_button()
    app.video_annotation.image_rotation_slider_bar_available()
    assert app.video_annotation.get_image_rotation_degree() == "15°"
    app.video_annotation.deactivate_iframe()
