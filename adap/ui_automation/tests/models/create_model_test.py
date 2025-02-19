"""
https://appen.atlassian.net/browse/QED-1464
Automate file upload with valid/invalid file format for models(smart workflow)
"""
import time
import pytest
from adap.api_automation.utils.data_util import *

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')


@pytest.mark.skip(reason="deprecated")
def test_create_models_with_valid_data(app):
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    app.mainMenu.models_page()
    app.navigation.click_link("Create Model")
    time.sleep(2)
    app.models.choose_model_template_by_name('Label Pixels in Street Scene Images')

    app.verification.text_present_on_page("Works Before")
    app.verification.text_present_on_page("cml:image_segmentation")
    app.verification.text_present_on_page("Input columns")
    app.verification.text_present_on_page("image_url")
    app.verification.text_present_on_page("Output columns")
    app.verification.text_present_on_page("predicted_image_url")

    data_file = get_data_file("/models/valid_data.csv")
    app.job.data.upload_file(data_file, wait_time=5)
    app.models.wait_until_data_load(interval=2, max_wait_time=90)
    iframe_num = app.models.get_number_iframes_on_page()
    assert iframe_num == 5


@pytest.mark.skip(reason="deprecated")
def test_create_models_with_invalid_data(app_test):
    app_test.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    app_test.mainMenu.models_page()
    app_test.navigation.click_link("Create Model")
    time.sleep(2)
    app_test.models.choose_model_template_by_name('Label Pixels in Street Scene Images')

    data_file = get_data_file("/models/invalid_data.json")
    app_test.job.data.upload_file(data_file, wait_time=5)
    app_test.verification.text_present_on_page("Error: wrong file type")



