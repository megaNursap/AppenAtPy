"""
https://appen.atlassian.net/browse/QED-1761
"""

import time
from adap.api_automation.utils.data_util import *

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')

pytestmark = pytest.mark.regression_core

@pytest.mark.skipif(not pytest.running_in_preprod_subset, reason="Data and react migration not in Staging")
def test_team_edit_page(app):
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    time.sleep(2)
    app.mainMenu.account_menu("Customers")
    app.navigation.click_link("Users")
    user_email_to_be_updated = get_user_email('test_edit_team')
    team_id = get_user_team_id('test_edit_team')
    app.user.search_user_and_go_to_team_page(user_email_to_be_updated, team_id)
    app.user.click_edit_team()

    # get original value
    original_team_plan = app.user.get_team_plan()
    original_team_name = app.user.get_value_for_team('name')
    original_project_number = app.user.get_value_for_team('projectNumber')
    original_markup = app.user.get_value_for_team('markup')
    original_replenishthreshold = app.user.get_value_for_team('replenishThreshold')

    # new value, get them ready for assert purpose after updating
    faker = Faker()
    new_team_plan = 'free plans'
    user_name = (faker.name() + faker.zipcode()).replace(' ', '')
    new_team_name = "{user_name}@appen.com".format(user_name=user_name)
    new_project_number = 'PN1102'
    new_markup_replenishthreshold = random.randint(1, 5)

    # update to be new value
    app.user.update_team_plan(new_team_plan)
    app.user.update_value_for_team('name', new_team_name)
    app.user.update_value_for_team('markup', new_markup_replenishthreshold)
    app.user.update_value_for_team('projectNumber', new_project_number)
    app.user.update_value_for_team('replenishThreshold', new_markup_replenishthreshold)
    app.user.update_feature_flag_or_additional_role('Scripts Enabled')
    app.user.update_feature_flag_or_additional_role('active_learning_client')
    app.navigation.click_btn('Save Changes')
    time.sleep(2)

    # after update, go to edit team page again to verify the value is the one we updated
    app.user.click_edit_team()
    assert new_team_plan == app.user.get_team_plan()
    assert new_team_name == app.user.get_value_for_team('name')
    assert new_project_number == app.user.get_value_for_team('projectNumber')
    assert str(new_markup_replenishthreshold) == app.user.get_value_for_team('markup')
    assert str(new_markup_replenishthreshold) == app.user.get_value_for_team('replenishThreshold')

    # update value back to the original one for next automation run
    app.user.update_team_plan(original_team_plan)
    app.user.update_value_for_team('name', original_team_name)
    app.user.update_value_for_team('markup', original_markup)
    app.user.update_value_for_team('projectNumber', original_project_number)
    app.user.update_value_for_team('replenishThreshold', original_replenishthreshold)
    app.navigation.click_btn('Save Changes')
    time.sleep(2)