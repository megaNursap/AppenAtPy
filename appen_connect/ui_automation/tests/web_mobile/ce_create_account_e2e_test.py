import random
import re
import time

import pytest
from faker import Faker

from adap.api_automation.utils.data_util import generate_data_for_contributor_experience_user

pytestmark = pytest.mark.regression_ac_web_mobile

faker = Faker()


@pytest.fixture(scope="module", autouse=True)
def open_sign_up_page(app):
    app.ac_user.sign_up_contributor_experience()

@pytest.mark.ac_ui_smoke
def test_ce_e2e_sign_up_flow(app, open_sign_up_page):
    user_data = generate_data_for_contributor_experience_user()

    app.sign_up_web_mobile.create_uses(user_data)

    app.navigation.click_bytext("Create Account")
    app.verification.text_present_on_page("Verify E-mail")
    app.sign_up_web_mobile.sign_up_page.send_verification_code("999999")
    app.navigation.click_btn("Verify E-mail")
    time.sleep(2)
    app.ac_user.login_as(user_name=user_data['email'], password=user_data['password'], open_login_page=False)
    app.navigation.click_btn("Set Up My Account")
    app.ce_account_setup.accept_consent()

    app.ce_account_setup.set_about_you_info("English", "United States of America")
    app.ce_account_setup.set_social_media('Instagram', 'https://instagram.com/user_abooutY')

    app.navigation.click_btn("Continue")

    app.ce_account_setup.set_contact_info(user_data, receive_mail=True)

    app.navigation.click_btn("Finish")

    app.verification.text_present_on_page("Contact", is_not=False)

    # app.verification.current_url_contains('projects-placeholder')

    # PROFILE test
    app.ac_user.sign_up_contributor_experience(endpoint='/profile')

    app.verification.text_present_on_page(user_data['email'])
    app.verification.text_present_on_page(user_data['firstname'])
    app.verification.text_present_on_page(user_data['lastname'])
    app.verification.text_present_on_page(user_data['primary_language'])
    app.verification.text_present_on_page(user_data['country'])
    app.verification.text_present_on_page(user_data['state'])


    app.verification.text_present_on_page('Add languages you speak and sign languages you know to unlock more task opportunities.')
    app.verification.text_present_on_page('Additional Languages')
    app.verification.text_present_on_page('Add languages you speak and/or sign languages you know.')
    app.verification.text_present_on_page('Translation Experience')
    app.verification.text_present_on_page('Language pairs that I can translate (from my additional languages).')

#     # add additional languages
#     app.ce_profile.open_tab('LANGUAGES')
#     app.navigation.click_btn('Add additional Language')
#     app.ce_profile.languages.add_additional_language(locale_lang='German',
#                                                      lang_region='Germany',
#                                                      spoken_fluency='Fluent',
#                                                      writen_fluency='Fluent')
#
#     app.ce_profile.languages.add_additional_language(locale_lang='Dutch',
#                                                      lang_region='Belgium',
#                                                      spoken_fluency='Near Native',
#                                                      writen_fluency='Near Native',
#                                                      action='Save Changes')
#
#     lang_data = app.ce_profile.languages.get_additional_languages()
#     assert lang_data == {'LANGUAGE 1': {'locale_language': 'German (Germany)',
#                                         'spoken': 'Fluent',
#                                         'written': 'Fluent'},
#                          'LANGUAGE 2': {'locale_language': 'Dutch (Belgium)',
#                                         'spoken': 'Near Native',
#                                         'written': 'Near Native'}}
#
#     # add translation experience
#     app.navigation.click_btn('Add translation Pair')
#
#     app.ce_profile.languages.add_translation_experience(from_lang='German (Germany)',
#                                                         to_lang='English (United States of America)',
#                                                         reverse=True)
#
#     app.ce_profile.languages.add_translation_experience(from_lang='English (United States of America)',
#                                                         to_lang='Dutch (Belgium)',
#                                                         action='Save Changes')
#
#     transl_data = app.ce_profile.languages.get_translation_experience()
#     print(transl_data)
#
#     app.ce_profile.open_tab('PERSONAL INFO')
#
#     personal_info = app.ce_profile.personal_info.get_user_personal_info()
#     print('personal_info', personal_info)
#
#     app.ce_profile.personal_info.click_edit_section('Contact')
#     app.verification.text_present_on_page('Contact')
#     app.verification.text_present_on_page('Home address and mobile phone number.')
#     app.verification.text_present_on_page('Home Address')
#     app.verification.text_present_on_page('Phone Number')
#
#     home_address = app.ce_profile.personal_info.get_home_address()
#     print("homee ", home_address)
#
#     current_phone = re.sub('[^A-Za-z0-9]+', '', app.ce_profile.personal_info.get_phone_number())
#     new_phone = current_phone[1:-2] + '00'
#     app.ce_profile.personal_info.enter_phone_number(new_phone, action='Save Changes')
#
#     personal_info_updated = app.ce_profile.personal_info.get_user_personal_info()
#     current_phone = re.sub('[^A-Za-z0-9]+', '', personal_info_updated['contact'][1])
#     assert new_phone == current_phone[1:]
#
#     app.ce_profile.open_tab('MORE ABOUT ME')
#     app.verification.text_present_on_page('We want to present you more project opportunities that match your profile and skillset.')
#     app.verification.text_present_on_page('To do so we must shake hands on you answering some demographic questions.')
#
#     app.navigation.click_btn("Let\'s Do it!")
#     app.navigation.click_btn('Accept')
#         # add verification for disclamer
#
#     all_category = app.ce_profile.more_about_me.get_all_categories()
#     print(all_category)
#
#     app.ce_profile.more_about_me.click_edit_answers_for_category('Appen Work')
#     time.sleep(4)
#     questions = app.ce_profile.more_about_me.get_all_questions_for_category()
#     print(questions)
#     assert questions == [
#         "WHY DID YOU CHOOSE TO JOIN APPEN?",
#         "ROUGHLY WHAT PERCENTAGE OF YOUR EARNINGS DO YOU ESTIMATE COMES FROM APPEN?",
#         "WHAT WAS YOUR HOUSEHOLD INCOME BEFORE YOU JOINED APPEN?",
#         "WHAT TYPE OF WORK COMMITTMENTS ARE YOU LOOKING FOR FROM APPEN?",
#         "HOW MUCH WORK ARE YOU CURRENTLY RECEIVING FROM APPEN?",
#         "WHAT TYPE OF PROJECTS/WORK DO YOU HAVE AN INTEREST IN?",
#         "HAS WORKING WITH APPEN HELPED YOU TO GET OTHER WORK?",
#         "WHAT TYPE OF INCENTIVES/ REWARDS WOULD YOU LIKE RECEIVE FROM YOUR WORK WITH APPEN?",
#         "WHAT TYPE OF WORKSPACE DO YOU USE WHEN WORKING FOR APPEN?"
#     ]
#
#     app.ce_profile.more_about_me.answer_question(question='Why did you choose to join Appen?',
#                                                  answers=['There is no other available work for me'],
#                                                  question_type='radio_btn',
#                                                  )
#
#     app.ce_profile.more_about_me.answer_question(question='Roughly what percentage of your earnings do you estimate comes from Appen?',
#                                                  answers=['25%-50%'],
#                                                  question_type='radio_btn',
#                                                  action='Save Changes')
#
#     app.ce_profile.more_about_me.click_edit_answers_for_category('Family & Me')
#     time.sleep(4)
#     app.ce_profile.more_about_me.answer_question(
#         question='In which country were you born?',
#         answers='Albania',
#         question_type='dropdown',
#         action='Save Changes')
#
#     appen_work = app.ce_profile.more_about_me.get_progress_for_category('Appen Work')
#     family = app.ce_profile.more_about_me.get_progress_for_category('Family & Me')
#
#     print(appen_work)
#     print(family)
#
#

