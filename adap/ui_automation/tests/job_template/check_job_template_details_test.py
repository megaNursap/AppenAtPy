"""
https://appen.atlassian.net/browse/QED-1760
"""

import time
from adap.api_automation.utils.data_util import *

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')

pytestmark = pytest.mark.regression_core


@pytest.mark.skipif(not pytest.running_in_preprod, reason="Only enabled in preprod")
def test_check_job_template_details(app):
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    time.sleep(2)
    job_template_id = [1]
    for template_id in job_template_id:
        url = 'https://client.%s.cf3.us/admin/job_templates/%s' % (pytest.env, template_id)
        app.navigation.open_page(url)
        app.verification.text_present_on_page('Template Description')
        app.verification.text_present_on_page('Input')
        app.verification.text_present_on_page('Output')
        app.verification.text_present_on_page('What Contributors See')
        app.verification.text_present_on_page('Sample Data This is the data format your template job will expect by default')
        # download sample data
        # app.navigation.click_btn('Download Sample Data')
        time.sleep(5)
        # tmp_files_dir = app.job.app.temp_path_file
        app.job_template.click_edit_template_link()
        # file_name = app.job_template.get_example_data_file_name()
        # app.verification.verify_file_present_in_dir(file_name, tmp_files_dir)
        # update job template description
        original_description = app.job_template.get_job_template_description()
        app.job_template.edit_job_template(new_description='contributors filter and analyze text')
        updated_description = app.job_template.get_job_template_description()
        assert 'contributors filter and analyze text' in updated_description
        # update the description back to original one
        app.job_template.edit_job_template(new_description=original_description)
        final_description = app.job_template.get_job_template_description()
        assert original_description == final_description



