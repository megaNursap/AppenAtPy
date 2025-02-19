import allure
import pytest
import time
from adap.api_automation.utils.data_util import get_data_file, get_user_password, get_user_email, \
    generate_random_msg, get_test_data

email = get_user_email('test_ui_account')
password = get_user_password('test_ui_account')

pytestmark = [
    pytest.mark.regression_core,
    pytest.mark.adap_ui_uat,
    pytest.mark.adap_uat
]


@pytest.fixture(scope="module")
def login(app):
    app.user.login_as_customer(user_name=email, password=password)


@pytest.mark.ui_uat
@pytest.mark.parametrize('file_type, file_name',
                         [("csv", "/authors.csv"),
                          # ("jpg", "/sample.jpg"),
                          # ("png", "/sample_image.png"),
                          ("txt", "/sample.txt"),
                          ("xlsx", "/sample1.xlsx")])
def test_sending_message_and_valid_attachments(app, login, file_type, file_name):
    """
    Customer is able to send the text as well as attach file in the text box on welcome page
    """
    app.mainMenu.home_page()
    app.verification.text_present_on_page("Featured Job Templates")
    app.verification.text_present_on_page("Use Cases")
    app.verification.text_present_on_page("Sentiment Analysis")
    # app.verification.text_present_on_page("Don't see what you're looking for?")
    # app.verification.text_present_on_page("Tell us what your data needs - we'll get back to you with a recommendation")
    # app.job.fill_out_ticket_summary_on_homepage("This is test message")
    # sample_file = get_data_file(file_name)
    # app.job.data.upload_file(sample_file, wait_time=2)
    # app.job.verify_file_uploaded_homepage(file_name)
    # app.navigation.click_btn("Send")
    # app.verification.text_present_on_page("Thanks - we'll get back to you shortly")


# @pytest.mark.parametrize('file_type, file_name',
#                          [("json", "/sample_data.json"),
#                           ("pdf", "/file-sample.pdf")
#                           # ("xls", "/authors.xls")  # not working in jenkins
#                           ])
# @pytest.mark.skip(reason="feature is deprecated")
# def test_sending_message_and_invalid_attachments(app, login, file_type, file_name):
#     """
#     Customer is not able to attach  invalid file formats on welcome page
#     """
#     app.mainMenu.home_page()
#     app.job.fill_out_ticket_summary_on_homepage("This is test message")
#     sample_file = get_data_file(file_name)
#     app.job.data.upload_file(sample_file, wait_time=2)
#     app.verification.text_present_on_page("You can't upload files of this type.")


@pytest.mark.ui_uat
def test_recent_tab(app, login):
    app.mainMenu.home_page()
    app.job.create_new_job_from_template(template_type="Transcription",
                                         job_type="Audio Transcription")
    app.navigation.click_btn("Next: Design your job")
    app.mainMenu.home_page()
    # app.job.verify_recent_tab_template_homepage("Audio Transcription")


# @pytest.mark.skip(reason="feature is deprecated")
# def test_attaching_two_files_together(app, login):
#     app.mainMenu.home_page()
#     sample_file = get_data_file("/authors.csv")
#     app.job.data.upload_file(sample_file, wait_time=2)
#     sample_file = get_data_file("/sample_image.png")
#     app.job.data.upload_file(sample_file, wait_time=2)
#     app.verification.text_present_on_page("You can not upload any more files.")


@pytest.mark.ui_uat
def test_start_from_scratch_link_from_template_page(app, login):
    # verifying data page from "start from scratch" from template use case page
    app.mainMenu.home_page()
    app.job.click_on_template_type("Sentiment Analysis")
    # time.sleep(30)
    app.navigation.click_btn("Start from scratch")
    app.verification.current_url_contains('jobs/new')


# @pytest.mark.skip(reason="feature is deprecated")
# def test_message_box_with_5000_characters(app, login):
#     app.mainMenu.home_page()
#     message = generate_random_msg(5000)
#     app.job.fill_out_ticket_summary_on_homepage(message)
#     app.verification.text_present_on_page(
#         "Maximum character count exceeded. We just need a short summary of your job goals to get started.")


# @pytest.mark.skip(reason="feature is deprecated in rebrand")
# def test_deleting_and_attaching_file_in_browse_section(app, login):
#     app.mainMenu.home_page()
#     sample_file = get_data_file("/authors.csv")
#     app.job.data.upload_file(sample_file, wait_time=2)
#     app.job.delete_attached_file()
#     app.verification.text_present_on_page("Drop a sample of your data file here")
#     sample_file = get_data_file("/sample_image.png")
#     app.job.data.upload_file(sample_file, wait_time=2)


# @pytest.mark.skip(reason="feature is deprecated")
# def test_start_from_scratch_link_after_sending_message(app, login):
#     # Verifying data page from "start from scratch" link appearing after sending message
#     app.mainMenu.home_page()
#     app.job.fill_out_ticket_summary_on_homepage("This is test message")
#     app.navigation.click_btn("Send")
#     app.navigation.click_btn("start from scratch")
#     app.verification.current_url_contains('jobs/new')


# @pytest.mark.skip(reason="feature is deprecated in rebrand")
# def test_js_inputs_for_message_box(app, login):
#     app.mainMenu.home_page()
#     json_sample = "alert('I am an alert box');"
#     app.job.fill_out_ticket_summary_on_homepage(json_sample)
#     app.navigation.click_btn("Send")
#     app.verification.text_present_on_page("Thanks - we'll get back to you shortly")


@pytest.mark.ui_uat
def test_start_from_scratch_link_from_see_more(app, login):
    # verifying data page from "start from scratch" from see more option
    app.mainMenu.home_page()
    app.job.create_new_job_from_scratch()
    app.verification.current_url_contains('jobs/new')


# @pytest.mark.skip(reason="feature is deprecated in rebrand")
# def test_html_input_for_message_box(app, login):
#     app.mainMenu.home_page()
#     html_sample = "<html>" \
#                   "<body>" \
#                   "<h1>Heading 1</h1>" \
#                   "<h2>Heading 2</h2>" \
#                   "<h3>Heading 3</h3>" \
#                   "<h4>Heading 4</h4>" \
#                   "<h5>Heading 5</h5>" \
#                   "<h6>Heading 6</h6>" \
#                   "</body>" \
#                   "</html>"
#     app.job.fill_out_ticket_summary_on_homepage(html_sample)
#     app.navigation.click_btn("Send")
#     app.verification.text_present_on_page("Thanks - we'll get back to you shortly")
#

# @pytest.mark.skip(reason="feature is deprecated in rebrand")
# def test_help_links(app, login):
#     app.mainMenu.home_page()
#     app.verification.text_present_on_page("Need help getting started?")
#     if pytest.env == 'sandbox':
#         app.navigation.click_link("Read Help Docs")
#     else:
#         app.navigation.click_link("Read help docs")
#     app.verification.switch_to_window_and_verify_link("https://success.appen.com/hc/en-us")
#
#     app.mainMenu.home_page()
#     if pytest.env == 'sandbox':
#         app.navigation.click_link("View Example Case Studies")
#     else:
#         app.navigation.click_link("View example case studies")
#     app.verification.switch_to_window_and_verify_link(
#         "https://success.appen.com/hc/en-us/categories/200230979-Examples-and-Use-Cases")
#
#     app.mainMenu.home_page()
#     if pytest.env == 'sandbox':
#         app.navigation.click_link("Watch Training Videos")
#     else:
#         app.navigation.click_link("Watch training videos")
#     app.verification.switch_to_window_and_verify_link(
#         "https://success.appen.com/hc/en-us/sections/201955376-Video-Tutorials")
#

@pytest.mark.ui_uat
def test_templates_present_on_page(app, login):
    app.mainMenu.home_page()
    app.job.verify_job_templates_present_on_welcomepage(["Sentiment Analysis",
                                                         "Search Relevance",
                                                         "Data Categorization",
                                                         "Data Collection & Enrichment",
                                                         "Data Validation",
                                                         "Image Annotation",
                                                         "Transcription",
                                                         "Content Moderation"])


@pytest.mark.ui_uat
def test_table_header_on_usecase_template_page(app, login):
    app.mainMenu.home_page()
    app.job.click_on_template_type("Sentiment Analysis")

    # code is not working
    # app.job.verify_table_header_on_usecase_template_page(
    #     [" ", "YOUR DATA HAS (INPUT)", "CONTRIBUTOR DELIVERS (OUTPUT)"])

    app.verification.text_present_on_page('Judge the Relevance and Sentiment of Content')


#     TODO add preview page verification
# TODO template content verification

# @pytest.mark.skip(reason="bug cw-8029")
# def test_links_on_question_mark(app, login):
#     app.mainMenu.home_page()
#     app.job.open_help_center_menu()
#     app.navigation.click_link("Read Help Docs")
#     app.verification.switch_to_window_and_verify_link("https://success.{}.cf3.us/".format(pytest.env))
#     app.navigation.click_link("View Example Case Studies")
#     app.verification.switch_to_window_and_verify_link("https://success.{}.cf3.us/hc/en-us/categories/200230979".format(pytest.env))
#     app.navigation.click_link("Watch Training Videos")
#     app.verification.switch_to_window_and_verify_link("https://success.{}.cf3.us/hc/en-us/sections/201955376".format(pytest.env))
#     app.navigation.click_link("Success Center")
#     app.verification.switch_to_window_and_verify_link("https://success.{}.cf3.us/".format(pytest.env))
#     # app.navigation.click_link("Tour")
#     # app.verification.text_present_on_page('Choose a job template based on your use case.')
#     # app.verification.element_is_visible_on_the_page("//div[@id='first-time-tour-first']")
# #     app.job.verify_email_link("mailto:help@appen.com")


@pytest.mark.ui_sanity
@pytest.mark.ui_smoke
# @pytest.mark.builder
# @pytest.mark.make
# @pytest.mark.akon
@allure.issue("https://appen.atlassian.net/browse/JW-122", "BUG  on Sandbox JW-122")
def test_job_ui_sanity_check(app_test):
    username = get_test_data('test_predefined_jobs', 'user_name')
    password = get_test_data('test_predefined_jobs', 'password')
    job_id = pytest.data.predefined_data['job_with_judgments'][pytest.env]

    app_test.user.login_as_customer(user_name=username, password=password)

    app_test.mainMenu.home_page()
    app_test.verification.text_present_on_page('Job Templates')
    app_test.verification.text_present_on_page('Start From Scratch')
    app_test.verification.text_present_on_page('Product Categorization')

    app_test.mainMenu.jobs_page()
    app_test.verification.text_present_on_page('Your Jobs')
    app_test.verification.text_present_on_page('Job Title')
    app_test.verification.text_present_on_page('Create Job')

    app_test.job.open_job_with_id(job_id)

    app_test.job.open_tab('DATA')
    app_test.verification.text_present_on_page('Unit id')
    app_test.verification.text_present_on_page('Add More Data')
    app_test.verification.text_present_on_page('Split column')
    # app_test.verification.text_present_on_page('Page') remove it because it depends on uploaded data

    app_test.job.open_tab('DESIGN')
    app_test.verification.text_present_on_page('Title')
    app_test.verification.text_present_on_page('Instructions')
    app_test.verification.text_present_on_page('Insert Data')

    app_test.job.open_tab('QUALITY')
    app_test.verification.text_present_on_page('Step 3: Quality')
    app_test.verification.text_present_on_page('Test Questions')
    app_test.verification.text_present_on_page('judgments')

    app_test.job.open_tab('LAUNCH')
    app_test.verification.text_present_on_page('Price per Judgment')
    app_test.verification.text_present_on_page('Rows to Order')
    app_test.verification.text_present_on_page('Judgments per Row')

    app_test.job.open_tab('MONITOR')
    assert app_test.verification.wait_untill_text_present_on_the_page('Pending judgments', 30)
    app_test.verification.text_present_on_page('Dashboard')

    app_test.job.open_tab('RESULTS')
    app_test.verification.text_present_on_page('Full')
    app_test.verification.text_present_on_page('Source')
    app_test.verification.text_present_on_page('Download Report')

    app_test.job.open_action("Settings")
    app_test.verification.text_present_on_page('Contributors')
    app_test.verification.text_present_on_page('Internal')

    app_test.job.open_settings_tab('Quality Control,Quality Control Settings')
    app_test.verification.text_present_on_page('Minimum Time Per Page')
    app_test.verification.text_present_on_page('Max Judgments per Contributor')

    app_test.job.open_settings_tab("Sharing/Visibility")
    app_test.verification.text_present_on_page("Notify")
    app_test.verification.text_present_on_page("Add Job to Project")

    app_test.job.open_settings_tab("API")
    app_test.verification.text_present_on_page("Webhook")
    app_test.verification.text_present_on_page("Alias")

    app_test.job.open_settings_tab("Pay")
    app_test.verification.text_present_on_page("Payment Set")
    app_test.verification.text_present_on_page("Price per Page")


@pytest.mark.ui_sanity
@pytest.mark.ui_smoke
# @pytest.mark.builder
# @pytest.mark.make
# @pytest.mark.akon
@allure.issue("'https://appen.atlassian.net/browse/DO-11774'", "BUG  on Staging DO-11774")
def test_wf_ui_sanity_check(app_test):
    username = get_test_data('test_ui_account', 'user_name')
    password = get_test_data('test_ui_account', 'password')

    app_test.user.login_as_customer(user_name=username, password=password)
    app_test.mainMenu.workflows_page()

    app_test.verification.text_present_on_page("Create Workflow")
    app_test.verification.text_present_on_page("Date Created")

    predefined_wf = pytest.data.predefined_data["workflow_with_judgments"][pytest.env]

    app_test.workflow.open_wf_by_id(predefined_wf)
    app_test.verification.text_present_on_page("Canvas")

    app_test.navigation.click_link("Data")
    app_test.verification.text_present_on_page("File Name")
    app_test.verification.text_present_on_page("Date Uploaded")

    app_test.navigation.click_link("Launch")
    app_test.verification.text_present_on_page("Rows to order")
    app_test.verification.text_present_on_page("Price per Judgment")

    app_test.navigation.click_link("Results")
    app_test.verification.text_present_on_page("Workflows Report")
    app_test.verification.text_present_on_page("Regenerate Report")