import time

from allure_commons.types import AttachmentType

from adap.api_automation.services_config.make import Make
from adap.api_automation.utils.data_util import *
from adap.api_automation.services_config.builder import Builder
from adap.e2e_automation.services_config.contributor_ui_support import answer_questions_on_page
from adap.e2e_automation.services_config.job_api_support import generate_job_link
from adap.api_automation.services_config.in_platform_audit import IPA_API
from adap.ui_automation.utils.js_utils import element_to_the_middle

pytestmark = pytest.mark.regression_ipa

TEST_DATA = pytest.data.predefined_data['ipa_job']['ui_sample'].get(pytest.env, {}).get("sample_unit", "")
USER_EMAIL = get_user_email('test_account')
PASSWORD = get_user_password('test_account')
API_KEY = get_user_api_key('test_account')
_ipa = IPA_API(API_KEY)


@pytest.fixture(scope="module")
def ipa_job():
    copied_job = Builder(API_KEY)
    make = Make(API_KEY)
    copied_job_resp = copied_job.copy_job(TEST_DATA, "all_units")
    copied_job_resp.assert_response_status(200)

    job_id = copied_job_resp.json_response['id']
    # job_id = 2050645
    copied_job.job_id = job_id

    resp = make.get_jobs_cml_tag(job_id)
    cml_tags = resp.json_response
    copied_job.launch_job()
    copied_job.wait_until_status("running", max_time=60)

    return [job_id, cml_tags]


@pytest.mark.adap_ui_uat
@pytest.mark.adap_uat
@pytest.mark.dependency()
def test_submit_judgements_qa(app_test, ipa_job):
    app_test.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)

    job_link = generate_job_link(ipa_job[0], API_KEY, pytest.env)
    app_test.navigation.open_page(job_link)
    app_test.user.close_guide()

    app_test.user.task.wait_until_job_available_for_contributor(job_link)

    select_values = [select_value['name'] for select_value in ipa_job[1][1]['children']]
    checkboxes_values = [checkboxes_value['label'].lower() for checkboxes_value in ipa_job[1][0]['children']]
    answer_questions_on_page(app_test.driver, tq_dict='', mode='cml_checkboxes', values=checkboxes_values)
    answer_questions_on_page(app_test.driver, tq_dict='', mode='cml_select', values=select_values)

    app_test.job.judgements.click_submit_judgements()

    copied_job = Builder(API_KEY)
    copied_job.job_id = ipa_job[0]

    running_time = 0
    current_count = 0
    row_finalized = False
    while (current_count != 5) and (running_time < 4):
        time.sleep(15)
        res = copied_job.get_rows_and_judgements()
        current_count = len(res.json_response)
        print(res.json_response)
        if current_count == 5:
            row_finalized = True
        running_time += 1
    assert row_finalized, "Units have not been finalized"


@pytest.mark.adap_ui_uat
@pytest.mark.adap_uat
@pytest.mark.dependency(depends=["test_submit_judgements_qa"])
def test_view_details_sample_qa(app, ipa_job):
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(ipa_job[0])

    ipa_url = "https://client.{env}.cf3.us/jobs/{job}/audit".format(env=pytest.env, job=ipa_job[0])

    app.navigation.open_page(ipa_url)

    try:
        time.sleep(4)
        app.navigation.click_link("Generate Aggregations")
    except:
        pass

    # app.navigation.refresh_page()
    app.verification.wait_untill_text_present_on_the_page('Setup Audit', 300)
    app.navigation.click_link("Setup Audit")

    app.verification.text_present_on_page(
        "Setup your audit by selecting sample amount, source data, and question to display in audit preview")

    app.verification.text_present_on_page(
        "Select up to 3 different columns from your source data to display in the audit preview. "
        "Please note that at least 1 source data column is required for the preview.")

    app.verification.text_present_on_page("Select question to use as preview for audit. You can also filter rows by "
                                          "answers to the selected question.")

    app.job.ipa.title_present_in_modal_box('Audit Configuration')
    app.job.ipa.title_present_in_modal_box('Sample Units Amount', h3_title=False)
    app.job.ipa.title_present_in_modal_box('Data Source For Audit Preview', h3_title=False)
    app.job.ipa.title_present_in_modal_box('Question For Audit Preview', h3_title=False)

    app.job.ipa.customize_sampling_units(sampling_unit_amount=75)
    app.job.ipa.customize_data_source("image_url", "Image", action="Create")

    app.navigation.refresh_page()
    all_units = app.job.ipa.get_all_units_on_page()
    assert len(all_units) == 4


@pytest.mark.dependency(depends=["test_view_details_sample_qa"])
def test_sample_unit_bar_info_qa(app, ipa_job):
    all_units = app.job.ipa.get_all_units_on_page()
    side_sample_elem = app.job.ipa.get_side_bar_unit_information(['Sampled Units', 'Audited', 'Sample Job Accuracy'])
    side_finalized_elem = app.job.ipa.get_side_bar_information_finalized_units()
    assert side_sample_elem[0]['audited'] == side_finalized_elem[0]['audited']
    assert side_sample_elem[0]['job_accuracy'] == side_finalized_elem[0]['job_accuracy']
    assert int(side_sample_elem[0]['sampled units']) == len(all_units)
    assert int(side_finalized_elem[0]['total of units']) == int(len(all_units) / 0.75)


@pytest.mark.dependency(depends=["test_sample_unit_bar_info_qa"])
def test_filter_randomize_qa(app, ipa_job):
    app.navigation.refresh_page()
    units_on_page = app.job.ipa.get_all_units_on_page()
    ascending = all(l['unit_id'] == s['unit_id'] for l, s in
                    zip(units_on_page, sorted(units_on_page, key=lambda x: x['unit_id'])))
    assert ascending, "The units not in ascending order"
    app.job.ipa.sorting_by("Randomize")
    allure.attach(app.driver.get_screenshot_as_png(), name="Screenshot",
                  attachment_type=AttachmentType.PNG)
    units_on_page_after_randomize = app.job.ipa.get_all_units_on_page()
    ascending_after_randomize = all(l['unit_id'] == s['unit_id'] for l, s in
                    zip(units_on_page_after_randomize, sorted(units_on_page_after_randomize, key=lambda x: x['unit_id'])))
    assert not ascending_after_randomize, "The units in ascending order"
    descending_after_randomize = all(l['unit_id'] == s['unit_id'] for l, s in
                     zip(units_on_page, sorted(units_on_page, key=lambda x: x['unit_id'], reverse=True)))
    assert not descending_after_randomize, "The units in descending order"


@pytest.mark.dependency(depends=["test_sample_unit_bar_info_qa"])
def test_filter_unit_bar_info_qa(app, ipa_job):
    payload = {"filters":{"question":{"name":"what_type_of_food","values":[]},"audited":True}}
    all_units = app.job.ipa.get_all_units_on_page()

    unit_reject = all_units[0]['unit_id']

    app.job.ipa.view_details_by_unit_id(unit_reject)
    app.job.ipa.approve_question()
    app.navigation.click_link('Save and Close')

    app.job.ipa.filter_audit_status('Audited')
    app.job.ipa.apply_filters()
    expected_job_accuracy = _ipa.post_job_and_field_accuracy(ipa_job[0], payload).json_response['filter']['accuracy']
    filter_info = app.job.ipa.get_side_bar_unit_information(['Filtered Units', 'Audited', 'Filtered Job Accuracy'])
    assert int(filter_info[0]['audited']) == 1
    assert int(filter_info[0]['filtered units']) == 1
    assert "{:.0%}".format(expected_job_accuracy) == filter_info[0]['job_accuracy']
    app.job.ipa.remove_filters()

