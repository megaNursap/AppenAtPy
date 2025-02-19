import re
import time

import pytest

from adap.api_automation.utils.data_util import generate_data_for_contributor_experience_user
from appen_connect.api_automation.services_config.contributor_experience import ContributorExperience

pytestmark = pytest.mark.regression_ac_web_mobile


@pytest.fixture(scope="module")
def new_ce_account(app):
    user = ContributorExperience()
    user_data = generate_data_for_contributor_experience_user()
    res = user.post_create_user(email=user_data['email'], password=user_data['password'],
                                firstname=user_data['firstname'], lastname=user_data['lastname'])
    app.ac_user.sign_up_contributor_experience(endpoint="/account-setup")
    app.ac_user.login_as(user_name=res.json_response['email'], password=user_data['password'])
    app.navigation.click_btn("Set Up My Account")
    app.ce_account_setup.accept_consent()

    app.ce_account_setup.set_about_you_info("English", "United States of America")
    app.navigation.click_btn("Continue")

    app.ce_account_setup.set_contact_info(user_data, receive_mail=True)

    app.navigation.click_btn("Finish")
    return user_data


@pytest.mark.dependency()
def test_ce_profile_personal_info_landing_page(app, new_ce_account):
    app.navigation.open_page('https://contributor-experience.integration.cf3.us/profile')
    time.sleep(5)

    app.ce_profile.open_tab('PERSONAL INFO')

    app.verification.text_present_on_page('Contact')
    app.verification.text_present_on_page(new_ce_account['address'])
    app.verification.text_present_on_page('Social Media')
    app.verification.text_present_on_page('Your Feedback Matters')
    app.verification.text_present_on_page("We\'d love to hear from you! Share your feedback, ideas, or suggestions to "
                                          "help us improve your experience Let's work together to shape the future of"
                                          " Appen Connect.")


@pytest.mark.dependency(depends=["test_ce_profile_personal_info_landing_page"])
def test_ce_profile_edit_phone(app, new_ce_account):
    app.ce_profile.personal_info.click_edit_section('Contact')
    current_phone = re.sub('[^A-Za-z0-9]+', '', app.ce_profile.personal_info.get_phone_number())
    new_phone = current_phone[1:-2] + '00'
    app.ce_profile.personal_info.enter_phone_number(new_phone, action='Save Changes')

    personal_info_updated = app.ce_profile.personal_info.get_user_personal_info()
    current_phone = re.sub('[^A-Za-z0-9]+', '', personal_info_updated['contact'][1])
    assert new_phone == current_phone[1:]


@pytest.mark.dependency(depends=["test_ce_profile_edit_phone"])
def test_ce_profile_edit_social(app, new_ce_account):
    current_social = app.ce_profile.personal_info.get_user_personal_info()
    assert current_social['social_media'] == {'facebook': 'Not set',
                                              'instagram': 'Not set',
                                              'twitter': 'Not set',
                                              'linkedin': 'Not set'}

    app.ce_profile.personal_info.click_edit_section('Social Media')

    app.ce_profile.personal_info.enter_social_media({"facebook": "https://www.facebook.com/test",
                                                     "instagram": "https://www.instagram.com/test",
                                                     "twitter": "https://www.twitter.com/test",
                                                     "linkedin": "https://www.linkedin.com/test",
                                                     },
                                                    action="Save Changes")

    updated_social = app.ce_profile.personal_info.get_user_personal_info()
    assert updated_social['social_media'] == {'facebook': 'https://www.facebook.com/test',
                                              'instagram': 'https://www.instagram.com/test',
                                              'twitter': 'https://www.twitter.com/test',
                                              'linkedin': 'https://www.linkedin.com/test'}


@pytest.mark.dependency(depends=["test_ce_profile_edit_social"])
def test_ce_profile_share_feedback(app, new_ce_account):
    app.verification.verify_link_redirects_to('Share Your Feedback', 'https://t.maze.co/', new_window=True)


@pytest.mark.dependency(depends=["test_ce_profile_share_feedback"])
def test_ce_profile_settings_landing_page(app, new_ce_account):
    app.ce_profile.open_tab('SETTINGS')
    app.verification.text_present_on_page('Password')
    app.verification.text_present_on_page('Click the button to be taken to the change password page.')
    app.verification.text_present_on_page('Notifications')
    app.verification.text_present_on_page('Smartphone Validation')
    app.verification.text_present_on_page('Delete Account')
    app.verification.text_present_on_page(
        'Click the button to withdraw from your applications and permanently delete your account')
    app.verification.text_present_on_page('Terms & Consent')
    app.verification.text_present_on_page('Review all the terms, policy, consent forms and Appen privacy documents')


@pytest.mark.dependency(depends=["test_ce_profile_settings_landing_page"])
def test_ce_profile_settings_change_password(app, new_ce_account):
    app.navigation.click_btn('Change Password')
    print(new_ce_account)
    app.verification.current_url_contains('/auth/realms/QRP/login-actions')
    app.verification.text_present_on_page('Update password')
    app.verification.text_present_on_page('New Password')
    app.verification.text_present_on_page('Confirm password')

    app.navigation.browser_back()
    app.ce_profile.open_tab('SETTINGS')
    app.verification.text_present_on_page('Change Password')


@pytest.mark.dependency(depends=["test_ce_profile_settings_change_password"])
def test_ce_profile_settings_notification(app, new_ce_account):
    current_notification = app.ce_profile.settings.get_notifications()
    assert current_notification == {'RECRUITMENT': 'Not set', 'COMMUNITY UPDATES': 'Not set'}
    app.ce_profile.personal_info.click_edit_section('Notifications')
    app.verification.text_present_on_page('Recruitment')
    app.verification.text_present_on_page('Receive notifications from our recruiting team about new task '
                                          'opportunities that matches your profile.')
    app.verification.text_present_on_page(
        'Enable the options that you desire to receive in regards of Appen communication.')
    app.verification.text_present_on_page('Community Updates')
    app.verification.text_present_on_page('Receive notifications from our community. From tips, to feature releases '
                                          'and new training courses.')

    app.ce_profile.settings.enable_notification(recruitment=True, community_updates=True, action='Save Changes')

    current_notification = app.ce_profile.settings.get_notifications()
    assert current_notification == {'RECRUITMENT': 'Email', 'COMMUNITY UPDATES': 'Email'}

    app.ce_profile.personal_info.click_edit_section('Notifications')
    app.ce_profile.settings.enable_notification(community_updates=True, action='Save Changes')

    current_notification = app.ce_profile.settings.get_notifications()
    assert current_notification == {'RECRUITMENT': 'Email', 'COMMUNITY UPDATES': 'Not set'}


@pytest.mark.dependency(depends=["test_ce_profile_settings_notification"])
def test_ce_profile_settings_smartphone_validation(app, new_ce_account):
    app.navigation.click_btn('Validate your Smartphone')

    app.verification.text_present_on_page('Smartphone Validation')
    app.verification.text_present_on_page('The following smartphones are eligible to be added to your profile. You may only have a maximum of one of each type:')
    app.verification.text_present_on_page('Note: we have found certain QR code readers to be incompatible with our detection algorithm. If you receive an error message on your device regarding your barcode scanner, please try a different one.')
    # app.navigation.click_btn('Add Smartphone')
    app.verification.text_present_on_page("Scan this QR code with your smartphone\'s QR code reader.")
    app.navigation.click_btn('Back')


@pytest.mark.dependency(depends=["test_ce_profile_settings_smartphone_validation"])
def test_ce_profile_settings_terms_consent(app, new_ce_account):
    app.verification.text_present_on_page('Terms & Consent')
    app.navigation.click_btn('Review all the terms, policy, consent forms and Appen privacy documents.')
    app.verification.text_present_on_page('Confidentiality Agreement')
    app.verification.text_present_on_page('Bona Fide Occupational Qualification Disclosure')
    app.verification.text_present_on_page('Electronic Consent')
    app.navigation.click_btn('Back')


@pytest.mark.dependency(depends=["test_ce_profile_settings_terms_consent"])
def test_ce_profile_settings_delete_account(app, new_ce_account):
    app.navigation.click_btn('Delete Account')
    app.verification.text_present_on_page('Delete Account?')
    app.verification.text_present_on_page('Click the button to withdraw from your applications and permanently delete '
                                          'your account. Kindly take note that, any pending invoices cannot be '
                                          'processed for payment.')
    app.navigation.click_link('Delete Account', index=1)

    app.verification.text_present_on_page('Account Deleted')
    app.verification.text_present_on_page('Your account was deleted successfully.')
