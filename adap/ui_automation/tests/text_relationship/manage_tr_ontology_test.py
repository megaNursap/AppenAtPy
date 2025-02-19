"""
This test mainly focus on manage ontology class, it covers:
https://appen.atlassian.net/browse/QED-1310
1.add/edit/delete class
2.add/edit/delete relationship on ontology class
"""

from adap.api_automation.utils.data_util import *
from adap.ui_automation.services_config.text_relationship import create_text_relationship_job

pytestmark = [pytest.mark.text_relationship,
              pytest.mark.adap_ui_uat,
              pytest.mark.adap_uat,
              pytest.mark.regression_text_relationship]

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')
predefined_jobs = pytest.data.predefined_data


@pytest.fixture(scope="module", autouse=True)
def tx_job(tmpdir_factory, app):
    """
    Create Text Relationship job using output of a predefined Text Annotation job
    """
    tmpdir = tmpdir_factory.mktemp('data')
    job_id = create_text_relationship_job(tmpdir, API_KEY, predefined_jobs)
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    return job_id


@pytest.mark.dependency()
@pytest.mark.text_relationship
def test_upload_ontology_design(app, tx_job):
    """
    Verify requestor can upload ontology json to an existing Text Relationship job
    """
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(tx_job)

    app.job.open_tab('DESIGN')
    app.navigation.click_link('Manage Text Relationships Ontology')

    ontology_file = get_data_file('/text_relationship/ontology.json')
    app.ontology.upload_ontology(ontology_file)
    app.verification.text_present_on_page("Classes Created")


@pytest.mark.dependency(depends=["test_upload_ontology_design"])
@pytest.mark.text_relationship
# @pytest.mark.skip
def test_add_edit_delete_class(app, tx_job):
    """
    Verify requestor can add/update/delete a new ontology class
    """
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(tx_job)
    app.job.open_tab('DESIGN')
    app.navigation.click_link('Manage Text Relationships Ontology')

    app.ontology.add_class(title='newclass', color='#C1561A')
    app.ontology.search_class_by_name(class_name='newclass')

    app.ontology.edit_class(class_name='newclass', new_title='name updated')
    app.ontology.search_class_by_name(class_name='name updated')

    app.ontology.delete_class(class_name='name updated')
    app.ontology.search_class_by_name(class_name='name updated', found=False)


@pytest.mark.dependency(depends=["test_upload_ontology_design"])
@pytest.mark.text_relationship
# @pytest.mark.skip
def test_create_relationship_for_ontology(app, tx_job):
    """
    Verify requestor can successfully create a relationship for an ontology class.
    (Creating self relationship for this test scenario)
    """
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(tx_job)

    app.job.open_tab('DESIGN')
    app.navigation.click_link('Manage Text Relationships Ontology')
    app.ontology.open_class('name')
    app.ontology.add_relationship(name='new', connect_to='This Class')
    # validate
    app.ontology.open_class('name')
    saved_rel = app.ontology.find_relationship_by_name('new')
    assert saved_rel['name'] == 'new'
    assert saved_rel['connect_to'] == 'name'
    app.navigation.click_link('Cancel')


@pytest.mark.dependency(depends=["test_upload_ontology_design"])
@pytest.mark.text_relationship
# @pytest.mark.skip
def test_edit_relationship_for_ontology(app, tx_job):
    """
    Verify requestor can update name and connects_to fields of an existing relationship
    """
    # not stable, sometimes can not locate element
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(tx_job)

    app.job.open_tab('DESIGN')
    app.navigation.click_link('Manage Text Relationships Ontology')
    app.ontology.open_class('company')
    app.ontology.edit_relationship(name='test', update_name='updated', update_connect='This Class')
    app.ontology.open_class('company')
    new_name = app.ontology.find_relationship_by_name('updated')
    assert len(new_name) > 0, "New Relationship updated has not been found, it should be there, something goes wrong"
    app.navigation.close_modal_window()


@pytest.mark.dependency(depends=["test_upload_ontology_design"])
@pytest.mark.text_relationship
def test_delete_relationship_for_ontology(app, tx_job):
    """
    Verify requestor can delete existing relationship defined for an ontology class
    """
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(tx_job)

    app.job.open_tab('DESIGN')
    app.navigation.click_link('Manage Text Relationships Ontology')
    app.ontology.open_class('designation')
    app.ontology.delete_relationship(name='owned by')
