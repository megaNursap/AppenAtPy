"""
https://appen.atlassian.net/browse/QED-1515
This test covers:
1. Download full report (checked with team, agg report is not applicable for PLSS)
2. Verify full report
3. check force regenerate report feature
"""
import time
from adap.api_automation.utils.data_util import *
from adap.ui_automation.utils.selenium_utils import *

JOB_ID = pytest.data.predefined_data['plss'].get(pytest.env)

pytestmark = pytest.mark.regression_plss

USER_EMAIL = get_user_email('test_predefined_jobs')
PASSWORD = get_user_password('test_predefined_jobs')
API_KEY = get_user_api_key('test_predefined_jobs')

@pytest.mark.adap_ui_uat
@pytest.mark.adap_uat
@pytest.mark.skipif(not pytest.running_in_preprod, reason="Only enabled in preprod")
def test_manage_reports(app):
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(JOB_ID)

    app.job.open_tab("RESULTS")
    app.job.results.download_report('Full', JOB_ID)
    file_name_zip = "/" + app.job.results.get_file_report_name(JOB_ID, 'Full')
    full_file_name_zip = app.temp_path_file + file_name_zip

    unzip_file(full_file_name_zip)
    csv_name = str(full_file_name_zip)[:-4]

    _df = pd.read_csv(csv_name)
    assert 'annotation' in _df.columns
    assert 'image_url' in _df.columns

    random_row = random.randint(0, _df.shape[0] - 1)
    annotation_url = _df['annotation'][random_row]
    image_url = _df['image_url'][random_row]

    import requests
    # annotation_res = requests.get(annotation_url)
    # assert annotation_res.status_code == 200
    image_res = requests.get(image_url)
    assert image_res.status_code == 200
    os.remove(csv_name)
    os.remove(full_file_name_zip)

