"""
TR - UI Automation - Post job launch - Relationships
https://appen.atlassian.net/browse/QED-1296

TR - UI Automation - Post job launch - Ontology class
https://appen.atlassian.net/browse/QED-1295

TR - UI Automation - Judgements - Success or validation error
https://appen.atlassian.net/browse/QED-1292
"""
from adap.api_automation.services_config.builder import Builder as JobAPI
from adap.api_automation.utils.data_util import *
from adap.ui_automation.services_config.text_relationship import create_text_relationship_job
from adap.ui_automation.utils.pandas_utils import *
from adap.e2e_automation.services_config.job_api_support import generate_job_link


USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')
predefined_jobs = pytest.data.predefined_data

pytestmark = [pytest.mark.text_relationship,
              pytest.mark.regression_text_relationship]


@pytest.fixture(scope="module")
def tx_job(tmpdir_factory, app):
    """
    Create Text Relationship job using output of a predefined Text Annotation job, upload ontology json, and launch job
    """
    tmpdir = tmpdir_factory.mktemp('data')
    job_id = create_text_relationship_job(tmpdir, API_KEY, predefined_jobs, change_text=True)
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)

    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)

    app.job.open_tab('DESIGN')
    app.navigation.click_link('Manage Text Relationships Ontology')

    ontology_file = get_data_file('/text_relationship/ontology.json')
    app.ontology.upload_ontology(ontology_file)
    app.verification.text_present_on_page("Classes Created")

    app.job.open_action("Settings")

    app.driver.find_element('xpath',"//label[text()='External']").click()
    app.navigation.click_link('Save')

    app.job.open_tab('LAUNCH')
    app.navigation.click_link("Launch Job")

    job = JobAPI(API_KEY, job_id=job_id)

    job.wait_until_status('running',60)
    res = job.get_json_job_status()
    res.assert_response_status(200)
    assert 'running' == res.json_response['state'], "Job status: %s \n Expected status: %s" % (
        res.json_response['state'], "running")

    app.job.open_tab('DESIGN')
    app.navigation.click_link("Manage Text Relationships Ontology")

    return job_id

def test_add_ontology_for_launched_tr_job(app, tx_job):
    """
    Verify "Add Class" button is disabled after launch
    """
    app.verification.element_is('disabled', 'Add Class')


def test_upload_btn_ontology_for_launched_tr_job(app, tx_job):
    """
    Verify "Upload" button is disabled after launch
    """
    app.verification.element_is('disabled', 'Upload')


def test_settings_btn_ontology_for_launched_tr_job(app, tx_job):
    """
    Verify "Settings" button is disabled after launch
    """
    app.verification.element_is('disabled', 'Settings')


def test_delete_ontology__for_launched_tr_job(app, tx_job):
    """
    Verify users cannot delete ontology classes after launch
    """
    ontology_classes = app.ontology.get_all_group_labels()
    random_class = random.choice(ontology_classes)
    app.ontology.delete_class_icon_is_displayed(random_class)


def test_class_title_ontology_for_launched_tr_job(app, tx_job):
    """
    Verify that class title is disabled after launch
    """
    ontology_classes = app.ontology.get_all_group_labels()
    random_class = random.choice(ontology_classes)

    app.ontology.click_edit_class(random_class)
    assert app.verification.input_field_is_readonly("classTitle")
    app.navigation.refresh_page()


@pytest.mark.skip(reason="Bug on sandbox!")
def test_class_description_ontology_for_launched_tr_job(app, tx_job):
    """
    Verify users can edit the description of an ontology class after launch
    """
    ontology_classes = app.ontology.get_all_group_labels()
    random_class = random.choice(ontology_classes)
    app.ontology.click_edit_class(random_class)

    app.ontology.update_class_description("test test")
    app.navigation.click_link("Done")

    app.ontology.click_edit_class(random_class)
    assert app.ontology.get_class_description() == "test test"
    app.navigation.refresh_page()


def test_add_relationship_ontology_for_launched_tr_job(app, tx_job):
    """
    Verify users cannot add relationship types after launch
    """
    ontology_classes = app.ontology.get_all_group_labels()
    random_class = random.choice(ontology_classes)
    app.ontology.click_edit_class(random_class)

    app.verification.text_present_on_page("Add Relationship", is_not=False)
    app.navigation.refresh_page()


def test_relationship_name_ontology_for_launched_tr_job(app, tx_job):
    """
    Verify that requestor cannot update relationship name after launch
    """
    ontology_classes = app.ontology.get_all_group_labels()
    random_class = random.choice(ontology_classes)
    app.ontology.click_edit_class(random_class)

    assert app.verification.input_field_is_readonly("relationshipTypeName")
    app.navigation.refresh_page()


@allure.issue("https://appen.atlassian.net/browse/ADAP-2693", "ADAP-2693")
def test_submit_judgements_tr(app, tx_job):
    """
    Verify that validation error is thrown when no relationships are created for a data row
    """
    job_link = generate_job_link(tx_job, API_KEY, pytest.env)

    app.navigation.open_page(job_link)
    app.user.close_guide()

    app.user.task.wait_until_job_available_for_contributor(job_link)

    questions_on_page = app.text_relationship.get_number_iframes_on_page()

    for iframe in range(questions_on_page-1):

        app.text_relationship.activate_iframe_by_index(iframe)
        names = app.text_relationship.find_all_words_with_label('name')
        companies = app.text_relationship.find_all_words_with_label('company')

        app.text_relationship.add_text_relationship(first_word={"word": names[0], "label": "name"},
                                                    second_word={"word": companies[0], "label": "company"},
                                                    relation_type='owned by')
        app.annotation.deactivate_iframe()

    app.annotation.submit_page()

    # verify errors in the last iframe
    app.verification.text_present_on_page("Check below for errors!")

    app.text_relationship.activate_iframe_by_index(questions_on_page-1)
    app.verification.text_present_on_page("Annotation should have at least one relation")

    names = app.text_relationship.find_all_words_with_label('name')
    companies = app.text_relationship.find_all_words_with_label('company')

    app.text_relationship.add_text_relationship(first_word={"word": names[0], "label": "name"},
                                                second_word={"word": companies[0], "label": "company"},
                                                relation_type='owned by')
    app.annotation.deactivate_iframe()

    app.annotation.submit_page()
    time.sleep(2)

    app.verification.text_present_on_page('There is no work currently available in this task.')


@pytest.mark.dependency(depends=["test_submit_judgements_tr"])
def test_tr_reports(app_test, tx_job):
    """
    Verify that requestor can download full report and view the judgements in json format
    Verify that requestor can download aggregated report and view judgements in json format
    """

    app_test.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)

    app_test.mainMenu.jobs_page()
    app_test.job.open_job_with_id(tx_job)

    for report_type in ['Full', 'Aggregated']:

        app_test.job.open_tab("RESULTS")
        app_test.job.results.download_report(report_type, tx_job)

        file_name_zip = "/"+app_test.job.results.get_file_report_name(tx_job, report_type)
        full_file_name_zip = app_test.temp_path_file + file_name_zip

        unzip_file(full_file_name_zip)
        csv_name = str(full_file_name_zip)[:-4]

        _df = pd.read_csv(csv_name)
        assert 'text_relationship' in _df.columns

        random_row = random.randint(0, _df.shape[0]-1)
        url = _df['text_relationship'][random_row]

        import requests
        res = requests.get(url)
        assert res.status_code == 200
        assert len(res.json()['annotation']) > 0
        assert res.json()['annotation'][0]['from_span'] != {}
        assert res.json()['annotation'][0]['from_span']['classname'] == 'name'
        assert res.json()['annotation'][0]['to_span'] != {}
        assert res.json()['annotation'][0]['to_span']['classname'] == 'company'

        assert res.json()['annotation'][0]['name'] == 'owned by'
        assert res.json()['annotation'][0]['annotated_by'] == 'human'

        os.remove(csv_name)
        os.remove(full_file_name_zip)





