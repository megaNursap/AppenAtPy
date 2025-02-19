"""
https://appen.atlassian.net/browse/QED-1515
This test covers:
manage toolbar
"""
import time
from adap.api_automation.utils.data_util import *
from adap.ui_automation.services_config.plss import create_plss_job
from adap.ui_automation.utils.selenium_utils import *
from adap.data import annotation_tools_cml as data

pytestmark = [pytest.mark.regression_plss, pytest.mark.fed_ui]

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')


@pytest.fixture(scope="module")
def tx_job(app):
    job_id = create_plss_job(app, API_KEY, data.plss_cml, USER_EMAIL, PASSWORD)
    return job_id


@pytest.mark.dependency()
def test_annotate_plss_toolbar(app_test, tx_job):
    app_test.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    app_test.mainMenu.jobs_page()
    app_test.job.open_job_with_id(tx_job)
    app_test.job.preview_job()
    time.sleep(15)
    app_test.plss.activate_iframe_by_index(0)
    time.sleep(10)
    app_test.plss.full_screen()
    # verify help menu
    app_test.plss.click_toolbar_button('help')
    # app_test.verification.text_present_on_page('Using this tool')
    app_test.verification.text_present_on_page('CANVAS')
    app_test.verification.text_present_on_page('TOOLS')
    app_test.verification.text_present_on_page('DRAWING')
    app_test.verification.text_present_on_page('Pan Mode')
    app_test.verification.text_present_on_page('Label Mode')
    app_test.verification.text_present_on_page('Polygon Tool')
    app_test.verification.text_present_on_page('Magic Wand Tool')
    app_test.verification.text_present_on_page('Paintbrush Tool')
    app_test.verification.text_present_on_page('Fill Tool')
    # verify help menu can be closed
    app_test.plss.close_help_menu()

    assert app_test.plss.button_is_disable('pan')
    assert not app_test.plss.button_is_disable('zoom_in')
    assert not app_test.plss.button_is_disable('zoom_out')
    assert app_test.plss.button_is_disable('reframe')
    assert not app_test.plss.button_is_disable('label')

    app_test.plss.click_toolbar_button('zoom_in')
    assert not app_test.plss.button_is_disable('pan')
    assert not app_test.plss.button_is_disable('zoom_out')
    assert not app_test.plss.button_is_disable('reframe')

    app_test.plss.click_toolbar_button('annotate')
    app_test.plss.choose_annotate_tool('Fill')
    app_test.plss.fill_image(300, 300)