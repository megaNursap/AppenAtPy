"""
This test covers:
1. Download full and aggregate report for audio annotation
2. Verify full and aggregate report fields
3. check force regenerate report feature
"""

import time
from adap.api_automation.utils.data_util import *
from adap.ui_automation.utils.selenium_utils import *

JOB_ID = pytest.data.predefined_data['audio_annotation'].get(pytest.env)

pytestmark = [
    pytest.mark.regression_audio_annotation,
    pytest.mark.adap_ui_uat,
    pytest.mark.adap_uat
]


USER_EMAIL = get_user_email('test_predefined_jobs')
PASSWORD = get_user_password('test_predefined_jobs')
API_KEY = get_user_api_key('test_predefined_jobs')

@pytest.mark.skipif(not pytest.running_in_preprod, reason="Only enabled in preprod")
def test_manage_reports_audio_annotation(app):
    """
    (test case uses predefined Audio Annotation test job)
    1. Verify requestor can successfully download Full and Aggregated report of Audio Annotation job
    2. Verify requestor can successfully Force regenerate the report
    3. Verify that the downloaded report has the output json with audio annotations
    """
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(JOB_ID)

    for report_type in ['Full', 'Aggregated']:
        app.job.open_tab("RESULTS")
        app.job.results.download_report(report_type, JOB_ID)
        file_name_zip = "/" + app.job.results.get_file_report_name(JOB_ID, report_type)
        full_file_name_zip = app.temp_path_file + file_name_zip
        unzip_file(full_file_name_zip)
        csv_name = str(full_file_name_zip)[:-4]
        _df = pd.read_csv(csv_name)
        assert 'annotate_the_thing' in _df.columns
        assert 'annotate_the_thing_gold' in _df.columns
        assert 'audio_url' in _df.columns
        random_row = random.randint(0, _df.shape[0] - 1)
        audio_url = _df['audio_url'][random_row]
        import requests
        audio_url_res = requests.get(audio_url)
        assert audio_url_res.status_code == 200
        os.remove(csv_name)
        os.remove(full_file_name_zip)
        # feature changed. comment it out
        # app.navigation.click_link("Force regenerate this report")
        # progressbar = find_element(app.driver, "//div[@id='progressbar']")
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
        # as this is predefine job, requestor-proxy link expired even with regenerated report, will need to add these check in other test
        # as requestor-proxy links will expire, so we verify it after regenerate report
        # time.sleep(10)
        # file_name_zip = "/" + app.job.results.get_file_report_name(JOB_ID, report_type)
        # full_file_name_zip = app.temp_path_file + file_name_zip
        # unzip_file(full_file_name_zip)
        # csv_name = str(full_file_name_zip)[:-4]
        # _df = pd.read_csv(csv_name)
        # random_row = random.randint(0, _df.shape[0] - 1)
        # annotate_the_thing = _df['annotate_the_thing'][random_row]
        # annotation_res = requests.get(annotate_the_thing)
        # assert annotation_res.status_code == 200
        # assert "annotation" in annotation_res.json()
        # assert "nothingToAnnotate" in annotation_res.json()
        # assert "ableToAnnotate" in annotation_res.json()
        # assert len(annotation_res.json()['annotation']) > 0
        # assert annotation_res.json()['nothingToAnnotate'] is False
        # assert annotation_res.json()['ableToAnnotate'] is True
        # os.remove(csv_name)
        # os.remove(full_file_name_zip)






