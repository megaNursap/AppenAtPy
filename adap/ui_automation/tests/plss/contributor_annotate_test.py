import time
from adap.api_automation.utils.data_util import *
from adap.ui_automation.services_config.plss import create_plss_job
from adap.ui_automation.utils.selenium_utils import *
from adap.data import annotation_tools_cml as data
from adap.e2e_automation.services_config.job_api_support import generate_job_link

pytestmark = [pytest.mark.regression_plss, pytest.mark.fed_ui]

USER_EMAIL = get_user_email('test_account')
PASSWORD = get_user_password('test_account')
API_KEY = get_user_api_key('test_account')
CONTRIBUTOR_EMAIL = get_user_email('test_contributor_task')
CONTRIBUTOR_PASSWORD = get_user_password('test_contributor_task')


@pytest.fixture(scope="module")
def tx_job(app):
    job_id = create_plss_job(app, API_KEY, data.plss_cml, USER_EMAIL, PASSWORD)
    return job_id

@pytest.mark.dependency()
def test_submit_judgments_without_annotation(app, tx_job):
    app.user.logout()
    job_link = generate_job_link(tx_job, API_KEY, pytest.env)
    app.navigation.open_page(job_link)
    app.user.task.login(CONTRIBUTOR_EMAIL, CONTRIBUTOR_PASSWORD)
    app.user.close_guide()
    time.sleep(2)
    app.user.task.wait_until_job_available_for_contributor(job_link)
    app.plss.submit_page()
    app.verification.text_present_on_page('No changes were made to the annotation')


# @pytest.mark.skip(reason="https://appen.atlassian.net/browse/DO-10755")
@pytest.mark.dependency(depends=["test_submit_judgments_without_annotation"])
def test_submit_judgments_with_annotation(app, tx_job):
    app.plss.activate_iframe_by_index(0)
    time.sleep(2)
    app.plss.draw_triangle(600, 360, 50, 0, 0, 50)
    app.plss.draw_triangle(20, 20, 20, 0, 0, 30)
    app.plss.deactivate_iframe()

    for i in range(1, 5):
        app.plss.activate_iframe_by_index(i)
        time.sleep(2)
        app.plss.draw_triangle(20, 20, 20, 0, 0, 20)
        app.plss.draw_triangle(20, 20, 20, 0, 0, 20)
        app.plss.deactivate_iframe()
        time.sleep(2)

    app.plss.submit_page()
    app.verification.wait_until_text_disappear_on_the_page("Validating submission", 60)
    app.verification.text_present_on_page('There is no work currently available in this task.')
