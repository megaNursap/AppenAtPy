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
def test_ce_profile_languages_page(app, new_ce_account):
    print(new_ce_account)
    # user = new_ce_account['email']
    # password = new_ce_account['password']
    # # app.navigation.open_page('https://contributor-experience.integration.cf3.us/profile')
    #
    # app.ac_user.login_as(user, password, open_login_page=False)
    app.navigation.open_page('https://contributor-experience.integration.cf3.us/profile')
    time.sleep(5)

    app.ce_profile.open_tab('LANGUAGES')
    app.verification.text_present_on_page(
        'Add languages you speak and sign languages you know to unlock more task opportunities.')
    app.verification.text_present_on_page('Additional Languages')
    app.verification.text_present_on_page('Add languages you speak and/or sign languages you know.')
    app.verification.text_present_on_page('Translation Experience')
    app.verification.text_present_on_page('Language pairs that I can translate (from my additional languages).')

    app.verification.verify_link_redirects_to('request it through your help section',
                                              'https://crowdsupport.appen.com/hc/en-us/requests/new',
                                              new_window=True)


@pytest.mark.dependency(depends=["test_ce_profile_languages_page"])
def test_ce_profile_languages_page_review_the_term(app, new_ce_account):
    app.verification.verify_link_redirects_to('Review the terms',
                                              'https://contributor-experience.integration.cf3.us/terms',
                                              new_window=False)

    app.verification.text_present_on_page('Terms & Consents')
    app.verification.text_present_on_page(
        'Review all Appen documents, including the ones you have already consented to.')
    app.verification.text_present_on_page('Confidentiality Agreement')
    app.verification.text_present_on_page('Bona Fide Occupational Qualification Disclosure')
    app.verification.text_present_on_page('Electronic Consent')

    #     TODO expend test coverage: verify agreement content and signed dates

    app.navigation.click_btn('Back')
    app.verification.text_present_on_page('Additional Languages')


@pytest.mark.dependency(depends=["test_ce_profile_languages_page_review_the_term"])
def test_ce_profile_add_1st_language(app, new_ce_account):
    """
    verify user is able to add additional language
    """
    assert not app.verification.button_is_disable('Add additional Language')
    assert app.verification.button_is_disable('Add translation Pair')

    app.navigation.click_btn('Add additional Language')

    app.verification.text_present_on_page('Add languages you speak and sign languages you know to unlock more task '
                                          'opportunities.')
    app.verification.text_present_on_page('NO ADDITIONAL LANGUAGES YET')

    app.ce_profile.languages.add_additional_language(locale_lang='Dutch',
                                                     lang_region='Netherlands',
                                                     spoken_fluency='Native or Bilingual',
                                                     writen_fluency='Near Native',
                                                     action='Save Changes')

    lang_data = app.ce_profile.languages.get_additional_languages()
    assert lang_data == {'LANGUAGE 1': {'locale_language': 'Dutch (Netherlands)',
                                        'spoken': 'Native or Bilingual',
                                        'written': 'Near Native'}}

    assert not app.verification.button_is_disable('Add translation Pair')


@pytest.mark.dependency(depends=["test_ce_profile_add_1st_language"])
def test_ce_profile_add_2nd_language(app, new_ce_account):
    """
    verify user is able to add 2nd additional language
    """

    app.ce_profile.languages.click_edit_section('Additional Languages')
    app.ce_profile.languages.add_additional_language(locale_lang='Italian',
                                                     lang_region='Italy',
                                                     spoken_fluency='Advanced',
                                                     writen_fluency='Advanced',
                                                     action='Save Changes')

    lang_data = app.ce_profile.languages.get_additional_languages()
    assert lang_data == {'LANGUAGE 1': {'locale_language': 'Dutch (Netherlands)',
                                        'spoken': 'Native or Bilingual', 'written': 'Near Native'},
                         'LANGUAGE 2': {'locale_language': 'Italian (Italy)',
                                        'spoken': 'Advanced', 'written': 'Advanced'}}


@pytest.mark.dependency(depends=["test_ce_profile_add_2nd_language"])
def test_ce_profile_add_language_not_saved(app, new_ce_account):
    """
    verify lang won't be saved if do not click 'Save Changes'
    """

    app.ce_profile.languages.click_edit_section('Additional Languages')
    app.ce_profile.languages.add_additional_language(locale_lang='Abkhazian',
                                                     lang_region='Georgia',
                                                     spoken_fluency='Advanced',
                                                     writen_fluency='Advanced')

    assert not app.verification.button_is_disable('Save Changes')
    app.navigation.click_btn('Back')

    lang_data = app.ce_profile.languages.get_additional_languages()
    assert lang_data == {'LANGUAGE 1': {'locale_language': 'Dutch (Netherlands)',
                                        'spoken': 'Native or Bilingual', 'written': 'Near Native'},
                         'LANGUAGE 2': {'locale_language': 'Italian (Italy)',
                                        'spoken': 'Advanced', 'written': 'Advanced'}}


@pytest.mark.dependency(depends=["test_ce_profile_add_language_not_saved"])
def test_ce_profile_languages_required_fields(app, new_ce_account):
    """
    verify Save Changes is disable until all data is provided
    """

    app.ce_profile.languages.click_edit_section('Additional Languages')

    app.ce_profile.languages.add_additional_language()
    assert app.verification.button_is_disable('Save Changes')

    app.ce_profile.languages.edit_additional_language(locale_lang='Abkhazian', index=3)
    assert app.verification.button_is_disable('Save Changes')

    app.ce_profile.languages.edit_additional_language(lang_region='Georgia', index=3)
    assert app.verification.button_is_disable('Save Changes')

    app.ce_profile.languages.edit_additional_language(spoken_fluency='Advanced', index=3)
    assert app.verification.button_is_disable('Save Changes')

    app.ce_profile.languages.edit_additional_language(writen_fluency='Advanced', index=3)
    assert not app.verification.button_is_disable('Save Changes')
    app.navigation.click_btn('Save Changes')

    lang_data = app.ce_profile.languages.get_additional_languages()
    assert lang_data == {'LANGUAGE 1': {'locale_language': 'Abkhazian (Georgia)', 'spoken': 'Advanced', 'written': 'Advanced'},
                         'LANGUAGE 2': {'locale_language': 'Dutch (Netherlands)', 'spoken': 'Native or Bilingual', 'written': 'Near Native'},
                         'LANGUAGE 3': {'locale_language': 'Italian (Italy)', 'spoken': 'Advanced', 'written': 'Advanced'}}



@pytest.mark.dependency(depends=["test_ce_profile_languages_required_fields"])
def test_ce_profile_languages_change(app, new_ce_account):
    """
    verify user is able to change locale
    """
    app.ce_profile.languages.click_edit_section('Additional Languages')
    time.sleep(2)
    app.ce_profile.languages.edit_additional_language(index=1,
                                                      locale_lang='Afar',
                                                      lang_region='Djibouti',
                                                      spoken_fluency='Intermediate',
                                                      writen_fluency='Beginner',
                                                      action='Save Changes')

    lang_data = app.ce_profile.languages.get_additional_languages()
    assert lang_data == {'LANGUAGE 1': {'locale_language': 'Afar (Djibouti)', 'spoken': 'Intermediate', 'written': 'Beginner'},
                         'LANGUAGE 2': {'locale_language': 'Dutch (Netherlands)', 'spoken': 'Native or Bilingual', 'written': 'Near Native'},
                         'LANGUAGE 3': {'locale_language': 'Italian (Italy)', 'spoken': 'Advanced', 'written': 'Advanced'}}


@pytest.mark.dependency(depends=["test_ce_profile_languages_change"])
def test_ce_profile_languages_delete(app, new_ce_account):
    """
    verify user is able to delete locale
    """

    app.ce_profile.languages.click_edit_section('Additional Languages')
    time.sleep(2)
    app.ce_profile.languages.delete_additional_language(1)
    app.verification.text_present_on_page('This language may affect your available project opportunities.')
    app.verification.text_present_on_page("By deleting this language, you\'ll no longer see projects that are "
                                          "targeted to this language.")
    app.navigation.click_btn('Delete')
    app.navigation.click_btn('Save Changes')
    lang_data = app.ce_profile.languages.get_additional_languages()
    assert lang_data == {'LANGUAGE 1': {'locale_language': 'Dutch (Netherlands)', 'spoken': 'Native or Bilingual', 'written': 'Near Native'},
                         'LANGUAGE 2': {'locale_language': 'Italian (Italy)', 'spoken': 'Advanced', 'written': 'Advanced'}}


@pytest.mark.dependency(depends=["test_ce_profile_languages_delete"])
def test_ce_profile_languages_duplicates(app, new_ce_account):
    """
    verify user is not able to save duplicated locales
    """

    app.ce_profile.languages.click_edit_section('Additional Languages')
    app.ce_profile.languages.add_additional_language(locale_lang='Italian',
                                                     lang_region='Italy',
                                                     spoken_fluency='Advanced',
                                                     writen_fluency='Advanced',
                                                     action='Save Changes')

    app.verification.text_present_on_page("There's two or more duplicated languages. "
                                          "Remove the duplications to be able to make changes.")

    app.navigation.click_btn('Back')


@pytest.mark.dependency(depends=["test_ce_profile_languages_duplicates"])
def test_ce_profile_languages_error_primary(app, new_ce_account):
    """
    verify user is not able to save primary language as an additional one
    """

    app.ce_profile.languages.click_edit_section('Additional Languages')
    app.ce_profile.languages.add_additional_language(locale_lang='English',
                                                     lang_region='United States of America',
                                                     spoken_fluency='Native or Bilingual',
                                                     writen_fluency='Native or Bilingual',
                                                     action='Save Changes')

    app.verification.text_present_on_page("You cannot add your primary language as an additional one.")
    app.navigation.click_btn('Back')


@pytest.mark.dependency(depends=["test_ce_profile_languages_duplicates"])
def test_ce_profile_add_translation_experience(app, new_ce_account):
    """
    verify user is able to add Translation Experience
    """
    app.navigation.click_btn('Add translation Pair')

    app.ce_profile.languages.add_translation_experience(from_lang='Dutch (Netherlands)',
                                                        to_lang='English (United States of America)',
                                                        reverse=True,
                                                        action='Save Changes'
                                                        )
    transl_data = app.ce_profile.languages.get_translation_experience()
    assert transl_data == {'TRANSLATION PAIR 1': {'from_language': 'Dutch (NL)', 'to_language': 'English (US)'}} \
           or transl_data == {'TRANSLATION PAIR 1': {'from_language': 'English (US)', 'to_language': 'Dutch (NL)'}}


@pytest.mark.dependency(depends=["test_ce_profile_add_translation_experience"])
def test_ce_profile_add_2nd_translation_experience(app, new_ce_account):
    """
       verify user is able to add 2nd Translation Experience
    """
    app.ce_profile.languages.click_edit_section('Translation Experience')
    app.navigation.refresh_page()
    app.ce_profile.languages.add_translation_experience(from_lang='Italian (Italy)',
                                                        to_lang='Dutch (Netherlands)',
                                                        action='Save Changes'
                                                        )
    transl_data = app.ce_profile.languages.get_translation_experience()

    assert transl_data['TRANSLATION PAIR 1'] in [{'from_language': 'Dutch (NL)',
                                                    'to_language': 'English (US)'},
                                                 {'from_language': 'Italian (IT)',
                                                  'to_language': 'Dutch (NL)'},
                                                 {'from_language': 'English (US)',
                                                  'to_language': 'Dutch (NL)'}
                                                 ]

    assert transl_data['TRANSLATION PAIR 2'] in [{'from_language': 'Dutch (NL)',
                                                    'to_language': 'English (US)'},
                                                 {'from_language': 'English (US)',
                                                  'to_language': 'Dutch (NL)'},
                                                 {'from_language': 'Italian (IT)',
                                                  'to_language': 'Dutch (NL)'}
                                                 ]


@pytest.mark.dependency(depends=["test_ce_profile_add_2nd_translation_experience"])
def test_ce_profile_translation_experience_not_saved(app, new_ce_account):
    app.ce_profile.languages.click_edit_section('Translation Experience')
    app.navigation.refresh_page()
    app.ce_profile.languages.add_translation_experience(from_lang='Italian (Italy)',
                                                        to_lang='English (United States of America)'
                                                        )
    app.navigation.click_btn('Back')
    transl_data = app.ce_profile.languages.get_translation_experience()
    assert transl_data == {'TRANSLATION PAIR 1': {'from_language': 'Dutch (NL)', 'to_language': 'English (US)'},
                           'TRANSLATION PAIR 2': {'from_language': 'Italian (IT)', 'to_language': 'Dutch (NL)'}}


@pytest.mark.dependency(depends=["test_ce_profile_translation_experience_not_saved"])
def test_ce_profile_translation_experience_edit(app, new_ce_account):
    app.ce_profile.languages.click_edit_section('Translation Experience')
    app.navigation.refresh_page()
    app.ce_profile.languages.edit_translation_experience(from_lang='Italian (Italy)',
                                                         to_lang='English (United States of America)',
                                                         index=2,
                                                         action='Save Changes')
    transl_data = app.ce_profile.languages.get_translation_experience()

    assert transl_data['TRANSLATION PAIR 1'] in [{'from_language': 'English (US)', 'to_language': 'Dutch (NL)'},
                                                 {'from_language': 'Dutch (NL)', 'to_language': 'English (US)'}]

    assert transl_data['TRANSLATION PAIR 2'] in [{'from_language': 'Italian (IT)', 'to_language': 'English (US)'},
                                                 {'from_language': 'English (US)', 'to_language': 'Dutch (NL)'},
                                                 {'from_language': 'Dutch (NL)', 'to_language': 'English (US)'}]


@pytest.mark.dependency(depends=["test_ce_profile_translation_experience_edit"])
def test_ce_profile_translation_experience_delete(app, new_ce_account):
    app.ce_profile.languages.click_edit_section('Translation Experience')
    app.navigation.refresh_page()
    app.ce_profile.languages.delete_translation_experience(1)
    app.navigation.click_btn('Delete')
    app.navigation.click_btn('Save Changes')

    transl_data = app.ce_profile.languages.get_translation_experience()
    assert transl_data == {'TRANSLATION PAIR 1': {'from_language': 'Italian (IT)', 'to_language': 'English (US)'}}


@pytest.mark.dependency(depends=["test_ce_profile_translation_experience_delete"])
def test_ce_profile_translation_experience_duplicate(app, new_ce_account):
    app.ce_profile.languages.click_edit_section('Translation Experience')
    app.navigation.refresh_page()
    app.ce_profile.languages.add_translation_experience(from_lang='Italian (Italy)',
                                                        to_lang='English (United States of America)',
                                                        action ='Save Changes')

    app.verification.text_present_on_page('Please, delete one of the duplicated pairs.')
    app.navigation.click_btn('Back')
    transl_data = app.ce_profile.languages.get_translation_experience()
    assert transl_data == {'TRANSLATION PAIR 1': {'from_language': 'Italian (IT)', 'to_language': 'English (US)'}}

