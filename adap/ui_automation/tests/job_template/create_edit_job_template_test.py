"""
https://app_testen.atlassian.net/browse/QED-1747
"""

import time
from adap.api_automation.utils.data_util import *

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')

pytestmark = pytest.mark.regression_core


@pytest.fixture(scope="module", autouse=True)
def tear_down(app):
    yield
    templates_name = ['this is updated template', 'automation testing for job template' ]
    for template in templates_name:
        app.navigation.open_page(app.user.customer.URL+"admin/job_templates")
        time.sleep(2)
        if app.job_template.find_job_template_by_tile(template):
            app.job_template.click_delete_icon_for_template_title(template)
            app.navigation.click_btn('Delete')
            time.sleep(2)


@allure.issue("https://appen.atlassian.net/browse/ADAP-2263", "Integration, Bug ADAP-2263")
@pytest.mark.adap_ui_uat
@pytest.mark.adap_uat
@pytest.mark.dependency()
@pytest.mark.skipif(not pytest.running_in_preprod, reason="Only enabled in preprod")
def test_create_valid_job_template(app):
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    time.sleep(2)
    app.mainMenu.account_menu("Templates")
    app.verification.current_url_contains('/job_templates')
    csv_file = get_data_file("/5rows.csv")
    """
    if template created successfully, url will update to be something like https://client.sandbox.cf3.us/job_templates/229/edit, 
    so we assert the returned url. Successful message is hard to catch.
    """
    new_url = app.job_template.create_new_template(title='automation testing for job template', description='a new template',
                                                   source_job_id=1309545, data_file=csv_file)
    assert 'edit' in new_url
    assert 'job_templates' in new_url


@pytest.mark.dependency(depends=["test_create_valid_job_template"])
@pytest.mark.skipif(not pytest.running_in_preprod, reason="Only enabled in preprod")
def test_edit_job_template(app):
    app.job_template.edit_job_template(new_title="this is updated template", new_description="new description", input_optional="new input", out_optional="new output", delete_data_file=True)
    assert app.job_template.get_job_template_title() == "this is updated template"
    assert app.job_template.get_job_template_description() == "new description"
    assert app.job_template.get_job_template_input() == "new input"
    assert app.job_template.get_job_template_output() == "new output"


@pytest.mark.skipif(not pytest.running_in_preprod, reason="Only enabled in preprod")
def test_create_job_template_invalid_source_jobid(app_test):
    app_test.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    time.sleep(2)
    app_test.mainMenu.account_menu("Templates")
    app_test.verification.current_url_contains('/job_templates')
    csv_file = get_data_file("/5rows.csv")
    message = app_test.job_template.create_new_template(title='template for invalid source id', description='a new template',
                                                        source_job_id=129, data_file=csv_file, invalid_source_job_id=True)
    assert message == "Isn't valid ID or isn't a template"