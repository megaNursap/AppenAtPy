"""
This test mainly focus on manage text relationship, it covers:
https://appen.atlassian.net/browse/QED-1161
https://appen.atlassian.net/browse/QED-1273
https://appen.atlassian.net/browse/QED-1160
1.add/edit/delete text relationship between spans
2.sidepanel elements check
3.some negative cases for managing relationship
"""

from adap.api_automation.utils.data_util import *
from adap.ui_automation.services_config.text_relationship import create_text_relationship_job

pytestmark = [pytest.mark.text_relationship,  pytest.mark.regression_text_relationship]

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')
predefined_jobs = pytest.data.predefined_data


@pytest.fixture(scope="module", autouse=True)
def tx_job(tmpdir_factory, app):
    """
    Create Text relationship job using output of a predefined Text Annotation job, and upload ontology json
    """
    tmpdir = tmpdir_factory.mktemp('data')
    job_id = create_text_relationship_job(tmpdir, API_KEY, predefined_jobs)
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)

    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)

    app.job.open_tab('DESIGN')
    app.navigation.click_link('Manage Text Relationships Ontology')

    ontology_file = get_data_file('/text_relationship/ontology.json')
    app.ontology.upload_ontology(ontology_file)
    app.verification.text_present_on_page("Classes Created")

    return job_id


@pytest.mark.text_relationship
def test_manage_relationship(app, tx_job):
    """
    1. Verify requestor can create/edit/delete relationship type in preview mode
    2. Verify sidepanel columns ('From', 'Relation', 'To')
    3. Verify annotated relationships are shown in sidepanel
    4. Verify that relationships are displayed in the same order as they are added
    """
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(tx_job)
    job_window = app.driver.window_handles[0]
    app.job.preview_job()

    # preview_url = 'https://client.%s.cf3.us/jobs/%s/preview_redirect' % (pytest.env, tx_job)
    # app.driver.get(preview_url)

    app.text_relationship.activate_iframe_by_index(0)
    app.text_relationship.full_screen()

    name_words = app.text_relationship.find_all_words_with_label('name')
    assert name_words == ['Sebastian', '2007']

    company_words = app.text_relationship.find_all_words_with_label('company')
    assert company_words == ['Udacity', 'Recode']

    no_words = app.text_relationship.find_all_words_with_label('new')
    assert no_words == []

    app.text_relationship.click_word('Sebastian', 'name')
    app.text_relationship.click_word('Udacity', 'company')
    app.text_relationship.select_relationship_type('owned by')

    # spira 582, verify headers
    app.text_relationship.get_headers(left='FROM', center='RELATION', right='TO')

    app.text_relationship.add_text_relationship(first_word={"word": "Sebastian", "label": "name"},
                                           second_word={"word": "CEOs", "label": "designation"},
                                           relation_type='title')

    app.text_relationship.add_text_relationship(first_word={"word": "Recode", "label": "company"},
                                                second_word={"word": "2007", "label": "name"},
                                                relation_type='employee')

    current_rel = app.text_relationship.get_list_of_relationships()
    assert len(current_rel) == 3
    assert current_rel[0] == {"from": "Sebastian",
                              "relation": "owned by",
                              "to": "Udacity"
                              }
    assert current_rel[1] == {"from": "Sebastian",
                              "relation": "title",
                              "to": "CEOs"
                              }
    assert current_rel[2] == {"from": "Recode",
                              "relation": "employee",
                              "to": "2007"
                              }

    #  edit relationship
    app.text_relationship.edit_text_relationship('Recode', '2007', 'TEST')
    el_relationship = app.text_relationship.search_text_relationship('Recode', '2007')
    value_relation = el_relationship.find_element('xpath',
        ".//div[@class='b-RelationshipsList-Relationship__relationshipTypeName']//span").text
    assert value_relation.casefold() == 'test'

    # delete one relationship
    before_delete = app.text_relationship.get_list_of_relationships()
    app.text_relationship.delete_text_relationship('Sebastian', 'CEOs')
    after_delete = app.text_relationship.get_list_of_relationships()
    assert len(after_delete) == len(before_delete) - 1
    """
    QED-1160, combine case together, if run separate, when run app.text_relationship.full_screen(),
    there is error as IndexError: list index out of range,need investigation
    """
    app.text_relationship.click_word('Sebastian', 'name')

    blocked = app.text_relationship.word_is_blocked('Udacity', 'company')
    assert blocked, "Word Udacity is not blocked"

    app.verification.text_present_on_page("Select the relation below:", is_not=False)

    app.text_relationship.click_word('Sebastian', 'name')
    app.verification.text_present_on_page("Select the relation below:", is_not=False)

    # Contributor can select an ending span only if a relationship exists with it
    app.text_relationship.click_word('2007', 'name')
    app.text_relationship.click_word('Sebastian', 'name')
    app.verification.text_present_on_page("Select the relation below:", is_not=False)

    app.text_relationship.full_screen()
    app.driver.close()
    app.navigation.switch_to_window(job_window)

