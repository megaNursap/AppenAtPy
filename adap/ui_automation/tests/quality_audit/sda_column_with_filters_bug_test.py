
from adap.api_automation.services_config.hosted_channel import HC
from adap.api_automation.services_config.make import Make
from adap.api_automation.utils.data_util import *
from adap.api_automation.services_config.builder import Builder

pytestmark = pytest.mark.regression_ipa

TEST_DATA = pytest.data.predefined_data['ipa_job']['ui_sample'].get(pytest.env, {}).get('sda', "")
USER_EMAIL = get_user_email('test_sda')
PASSWORD = get_user_password('test_sda')
API_KEY = get_user_api_key('test_sda')


@pytest.fixture(scope="module")
def ipa_job(app):
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    app.job.ipa.open_quality_audit_page(TEST_DATA)
    make = Make(API_KEY)
    resp = make.get_jobs_cml_tag(TEST_DATA)
    cml_tags = resp.json_response
    try:
        app.navigation.click_link("Generate Aggregations")
    except:
        pass

    if app.verification.wait_untill_text_present_on_the_page('Setup Audit', 5):
        app.navigation.click_link("Setup Audit")

        app.verification.text_present_on_page(
            "Select up to 3 different columns from your source data to display in the audit preview. "
            "Please note that at least 1 source data column is required for the preview.")

        app.job.ipa.customize_data_source("media_url", "Image", action="Continue")

    return cml_tags


def test_sda_data_render_on_grid_view(app, ipa_job):
    builder = Builder(API_KEY, env=pytest.env)
    hc_res = HC(API_KEY)
    resp = builder.get_json_job_status(TEST_DATA)

    actual_num_units = resp.json_response['units_count']

    expected_image_on_grid_view = app.job.ipa.get_sda_source_data()

    assert len(expected_image_on_grid_view) == actual_num_units
    for index in range(0, actual_num_units):
        assert "redirect?token" in expected_image_on_grid_view[index], "The secret url build incorrect"
        url = expected_image_on_grid_view[index].replace(builder.url, "")
        res = builder.service.get(url)
        res.assert_response_status(200)


def test_sda_data_render_on_view_details(app, ipa_job):
    first_unit = app.job.ipa.get_all_units_on_page()[0]['unit_id']
    app.job.ipa.view_details_by_unit_id(first_unit)
    expected_image_on_view_detail = app.job.ipa.get_sda_source_data(att='class', att_value='custom-css')
    assert 1 == len(expected_image_on_view_detail)
    assert "redirect?token" in expected_image_on_view_detail[0], "The secret url build incorrect"
