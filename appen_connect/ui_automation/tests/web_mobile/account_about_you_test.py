import random
import time

import pytest
from faker import Faker

from adap.api_automation.utils.data_util import get_test_data

pytestmark = pytest.mark.regression_ac_web_mobile

faker = Faker()


list_of_social_media = ['Facebook', 'Instagram', 'Twitter', 'Linked']


@pytest.fixture(scope='module', autouse=True)
def open_sign_up_page(app):
    user_setup_email = get_test_data("contributor_experience_about_you", "email")
    user_setup_password = get_test_data("contributor_experience_about_you", "password")
    app.ac_user.sign_up_contributor_experience(endpoint="/account-setup")
    app.ac_user.login_as(user_name=user_setup_email, password=user_setup_password, open_login_page=False)


@pytest.fixture(autouse=True)
def sign_agreements(app, open_sign_up_page):
    app.navigation.refresh_page()
    app.navigation.open_page('https://contributor-experience.integration.cf3.us/profile')
    time.sleep(5)

    # app.navigation.click_btn("Set Up My Account")
    # app.ce_account_setup.accept_consent()


def test_web_mobile_region_language_disabled(app, sign_agreements):
    """
    User could select region language until the primary language set up
    """
    app.ce_account_setup.verify_state_of_element("disabled", app.ce_account_setup.about_you_page.LANGUAGE_REGION)


# def test_web_mobile_primary_region_language(app, sign_agreements):
#     """
#     User could select just this language region that
#     most associated with the variety of primary language
#     """
#     app.ce_account_setup.about_you_page.set_primary_language('Ukrainian')
#     # app.ce_account_setup.about_you_page.set_region_language('Sweden')
#     app.ce_account_setup.about_you_page.check_social_media('hasTwitter')
#
#     region_language_value = app.ce_account_setup.about_you_page.get_region_language_text()
#     print(region_language_value)
#
#     app.verification.text_present_on_page('Ukrainian')
#
#
#     assert region_language_value == 'Select', "The region language Not default"
#
#     app.ce_account_setup.about_you_page.set_region_language('Ukraine')
#
#     app.verification.text_present_on_page("Ukraine")

#TODO change test baseed on new functionality
# def test_web_mobile_require_filed(app, sign_agreements):
#     """
#     User should set up Primary and Region Language
#     """
#     # app.ce_account_setup.about_you_page.set_primary_language('None')
#     app.ce_account_setup.verify_state_of_element("disabled", app.ce_account_setup.about_you_page.LANGUAGE_REGION)
#     app.ce_account_setup.about_you_page.check_social_media('hasInstagram')
#
#     assert len(app.ce_account_setup.about_you_page.get_error_message()) == 1
#     assert app.ce_account_setup.about_you_page.get_error_message()[0].text == "Required field"
#
#     app.ce_account_setup.about_you_page.set_primary_language('Italian')
#     app.ce_account_setup.verify_state_of_element("disabled", app.ce_account_setup.about_you_page.LANGUAGE_REGION)
#     app.ce_account_setup.about_you_page.set_region_language("None")
#     app.ce_account_setup.about_you_page.check_social_media('hasInstagram')
#
#     assert len(app.ce_account_setup.about_you_page.get_error_message()) == 1
#     assert app.ce_account_setup.about_you_page.get_error_message()[0].text == "Required field"


def test_web_mobile_set_all_fields_about_you(app, sign_agreements):
    """
    User could set all require and optional field
    """
    app.ce_account_setup.about_you_page.set_primary_language('English')
    app.ce_account_setup.about_you_page.set_region_language('United States of America')

    for social_media in list_of_social_media:
        app.ce_account_setup.about_you_page.check_social_media(social_media)
        app.ce_account_setup.about_you_page.set_optional_info(social_media.lower(), f"{social_media.lower()}.com/userName")
    app.ce_account_setup.about_you_page.check_business_name()
    app.ce_account_setup.about_you_page.set_optional_info('businessName', "User_business_name")

    app.verification.text_present_on_page("English")
    app.verification.text_present_on_page("United States of America")
    assert [app.ce_account_setup.about_you_page.get_optional_field_value(
        social_media.lower()) == f"{social_media.lower()}.com/userName"
            for social_media in list_of_social_media]
    assert app.ce_account_setup.about_you_page.get_optional_field_value('businessName') == "User_business_name"


def test_web_mobile_unchecked_optional_filed_about_you(app, sign_agreements):
    """
    User could unchecked optional filed
    """
    app.ce_account_setup.about_you_page.set_primary_language('Spanish')
    app.ce_account_setup.about_you_page.set_region_language('Spain')

    for social_media in list_of_social_media:
        app.ce_account_setup.about_you_page.check_social_media(social_media)
        app.ce_account_setup.about_you_page.set_optional_info(social_media.lower(), f"{social_media.lower()}.com/userName")
    app.ce_account_setup.about_you_page.check_business_name()
    app.ce_account_setup.about_you_page.set_optional_info('businessName', "User_business_name")

    assert app.ce_account_setup.about_you_page.get_optional_field_value(list_of_social_media[1].lower()) == f'{list_of_social_media[1].lower()}.com/userName'

    app.ce_account_setup.about_you_page.check_social_media(list_of_social_media[1])

    assert len(app.ce_account_setup.about_you_page.get_optional_field(list_of_social_media[1].lower())) == 0


