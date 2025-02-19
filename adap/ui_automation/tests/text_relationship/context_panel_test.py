"""
TR - UI - Automation - Context panel
https://appen.atlassian.net/browse/QED-1332
"""
from adap.api_automation.services_config.builder import Builder
from adap.api_automation.utils.data_util import *
from adap.ui_automation.services_config.text_relationship import create_text_relationship_job
from adap.ui_automation.utils.pandas_utils import *

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')
predefined_jobs = pytest.data.predefined_data

pytestmark = [pytest.mark.text_relationship,  pytest.mark.regression_text_relationship]

CONTEXT_CML ='<cml:text_relationships label="Your annotation:" validates="required" source-data="{{my_annotations}}" name="text relationship" context-column="text"/>'


@pytest.fixture(scope="module")
def tx_job(tmpdir_factory, app):
    """
    Create Text Relationship job using output of predefined Text Annotation job and upload ontology json
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

    return job_id


@pytest.mark.dependency()
def test_context_column_tag(app, tx_job):
    """
    Verify that text relationship job CML tag accepts ‘context-column’ attribute
    Verify context panel icon is shown in tool bar only when CML has context-from attribute
    """

    # verify no icon
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(tx_job)

    app.job.preview_job()

    app.text_relationship.activate_iframe_by_index(0)
    assert not app.text_relationship.context_btn_is_displayed()

    api = Builder(API_KEY)

    updated_payload = {'job': {'cml': CONTEXT_CML}}
    res = api.update_job(tx_job, updated_payload)
    res.assert_response_status(200)

    app.navigation.refresh_page()
    app.text_relationship.activate_iframe_by_index(0)
    assert app.text_relationship.context_btn_is_displayed()

    app.annotation.deactivate_iframe()


@pytest.mark.dependency(depends=["test_context_column_tag"])
def test_context_btn(app, tx_job):
    """
    Verify that clicking on the context icon, displays the context in the side panel and is scrollable
    Verify user can close the context panel
    """

    for i in range(4):
        app.text_relationship.activate_iframe_by_index(i)

        assert not app.text_relationship.context_btn_is_active()

        app.text_relationship.click_context_btn()

        assert app.text_relationship.context_btn_is_active()
        app.verification.text_present_on_page('Context')

        _context = app.text_relationship.get_current_context()
        if len(_context) > 5:
            # long text
            assert app.text_relationship.context_scrollbar_is_visible()
        else:
            assert _context in ['test0', 'test1', 'test2', 'test3']

        # close context
        app.text_relationship.click_context_btn()

        assert not app.text_relationship.context_btn_is_active()
        _context = app.text_relationship.get_current_context()
        assert _context == ""

        app.annotation.deactivate_iframe()


@pytest.mark.dependency(depends=["test_context_column_tag"])
def test_create_relationships_with_context_panel(app, tx_job):
    """
    Verify user can access relationship popup and create relationships when context panel is open
    """
    app.text_relationship.activate_iframe_by_index(0)

    app.text_relationship.click_context_btn()
    app.verification.text_present_on_page('Context')

    app.text_relationship.click_word('Sebastian', 'name')
    app.text_relationship.click_word('Udacity', 'company')
    app.text_relationship.select_relationship_type('owned by')

    app.text_relationship.click_context_btn()

    current_rel = app.text_relationship.get_list_of_relationships()
    assert current_rel[0] == {"from": "Sebastian",
                              "relation": "owned by",
                              "to": "Udacity"}






