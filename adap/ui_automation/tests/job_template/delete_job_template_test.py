"""
https://appen.atlassian.net/browse/QED-1749
"""

import time
from adap.api_automation.utils.data_util import *
from faker import Faker

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')

pytestmark = pytest.mark.regression_core


@pytest.fixture(scope="module", autouse=True)
def tx_template(app):
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    time.sleep(2)
    app.mainMenu.account_menu("Templates")
    app.verification.current_url_contains('/job_templates')
    csv_file = get_data_file("/5rows.csv")
    faker = Faker()
    name = faker.company()
    title_name = 'New Job Template For ' + name
    app.job_template.create_new_template(title=title_name,
                                         description='a new template',
                                         source_job_id=1309545, data_file=csv_file, use_cases_optional='Sentiment Analysis')
    return title_name

@pytest.mark.adap_ui_uat
@pytest.mark.adap_uat
@pytest.mark.skipif(not pytest.running_in_preprod, reason="Only enabled in preprod")
def test_delete_job_template(app, tx_template):
    app.job_template.click_breadcrumb_link('Templates')
    assert app.job_template.find_job_template_by_tile(tx_template)
    app.job_template.click_delete_icon_for_template_title(tx_template)
    app.navigation.click_btn('Cancel')
    assert app.job_template.find_job_template_by_tile(tx_template)

    app.job_template.click_delete_icon_for_template_title(tx_template)
    app.navigation.click_btn('Delete')
    time.sleep(2)
    assert not app.job_template.find_job_template_by_tile(tx_template)
