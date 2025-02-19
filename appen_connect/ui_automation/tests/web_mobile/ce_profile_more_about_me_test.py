import time

import pytest

from adap.api_automation.utils.data_util import generate_data_for_contributor_experience_user
from adap.ui_automation.utils.js_utils import scroll_to_page_bottom, scroll_to_element
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


def test_ce_profile_MAM_landing_page(app, new_ce_account):
    app.navigation.open_page('https://contributor-experience.integration.cf3.us/profile')
    time.sleep(5)

    app.ce_profile.open_tab('MORE ABOUT ME')
    # app.verification.text_present_on_page('We want to present you more project opportunities that match your profile and skillset.')
    # app.verification.text_present_on_page('To do so we must shake hands on you answering some demographic questions.')
    # app.navigation.click_btn("Let\'s Do it!")
    # el = app.driver.find_element('xpath',
    #                              '//div[text()="You understand that you may ask for a copy of this Informed Consent '
    #                              'Form. Facsimile signatures constitute original signatures for all purposes."]')
    # scroll_to_element(app.driver, el)
    # app.navigation.click_btn('Accept')
    app.verification.text_present_on_page('Data Inclusion & Diversity Policy')
    app.verification.text_present_on_page('At Appen, we help create Artificial Intelligence (AI) that works for and '
                                          'benefits everyone. The following questions are intended to help us '
                                          'evaluate the demographic distribution of our Crowd so that we can identify '
                                          'and address any representation gaps on our projects. Having a '
                                          'demographically diverse Crowd working on our projects helps our clients '
                                          'create more inclusive, relevant and accessible AI products. The questions '
                                          'that follow include in-depth questions that range from who you are, '
                                          'to where you live, your education and work experience, and how Appen fits '
                                          'into your life.')
    app.navigation.click_btn('Close')

    app.verification.text_present_on_page('Complete profile information to fasten up your task qualification process.')

    all_category = app.ce_profile.more_about_me.get_all_categories()
    expected = ['Appen Work', 'Entertainment & Activities', 'Environmental', 'Family & Me', 'Health & Medical', 'Home & Income', 'Politics', 'Social', 'Technologies & Communications', 'Transport', 'Work & Education']
    assert sorted(all_category) == sorted(expected)


def test_ce_profile_progress_before(app, new_ce_account):
    all_category = app.ce_profile.more_about_me.get_all_categories()

    for category in all_category:
        first_category = app.ce_profile.more_about_me.get_progress_for_category(category)
        assert first_category['progress'] == '0%'


def test_ce_profile_appen_work_questions(app, new_ce_account):
    app.ce_profile.open_tab('MORE ABOUT ME')
    app.ce_profile.more_about_me.click_edit_answers_for_category('Appen Work')

    questions = app.ce_profile.more_about_me.get_all_questions_for_category()
    assert questions == [
        "WHY DID YOU CHOOSE TO JOIN APPEN?",
        "ROUGHLY WHAT PERCENTAGE OF YOUR EARNINGS DO YOU ESTIMATE COMES FROM APPEN?",
        "WHAT WAS YOUR HOUSEHOLD INCOME BEFORE YOU JOINED APPEN?",
        "WHAT TYPE OF WORK COMMITTMENTS ARE YOU LOOKING FOR FROM APPEN?",
        "HOW MUCH WORK ARE YOU CURRENTLY RECEIVING FROM APPEN?",
        "WHAT TYPE OF PROJECTS/WORK DO YOU HAVE AN INTEREST IN?",
        "HAS WORKING WITH APPEN HELPED YOU TO GET OTHER WORK?",
        "WHAT TYPE OF INCENTIVES/ REWARDS WOULD YOU LIKE RECEIVE FROM YOUR WORK WITH APPEN?",
        "WHAT TYPE OF WORKSPACE DO YOU USE WHEN WORKING FOR APPEN?"
    ]

    app.navigation.click_btn('Back')


def test_ce_profile_answer_all_for_appen_work(app, new_ce_account):
    appen_work = app.ce_profile.more_about_me.get_progress_for_category('Appen Work')
    assert appen_work == {'questions': '9 questions', 'progress': '0%'}

    app.ce_profile.more_about_me.click_edit_answers_for_category('Appen Work')

    app.ce_profile.more_about_me.answer_question(question='Why did you choose to join Appen?',
                                                 answers=['There is no other available work for me'],
                                                 question_type='radio_btn',
                                                 )

    app.ce_profile.more_about_me.answer_question(question='Roughly what percentage of your earnings do you estimate comes from Appen?',
                                                 answers=['25%-50%'],
                                                 question_type='radio_btn')

    app.ce_profile.more_about_me.answer_question(
        question='What was your household income before you joined Appen?',
        answers='USD 25,000 - USD34,999 per year',
        question_type='dropdown')

    app.ce_profile.more_about_me.answer_question(
        question='What type of work committments are you looking for from Appen?',
        answers=['Part-time work (i.e. 20-30 hours per week)'],
        question_type='radio_btn')

    app.ce_profile.more_about_me.answer_question(
        question='How much work are you currently receiving from Appen?',
        answers=['Part-time work (i.e. 20-30 hours per week)'],
        question_type='radio_btn')

    app.ce_profile.more_about_me.answer_question(
        question='What type of projects/work do you have an interest in?',
        answers=['Linguistics'],
        question_type='radio_btn')

    app.ce_profile.more_about_me.answer_question(
        question='Has working with Appen helped you to get other work?',
        answers=['Yes'],
        question_type='radio_btn')

    app.ce_profile.more_about_me.answer_question(
        question='What type of opportunities has working with Appen enabled to get outside of Appen?',
        answers=['Part-time work (i.e. <20 hours per week)'],
        question_type='radio_btn')

    app.ce_profile.more_about_me.answer_question(
        question='What type of incentives/ rewards would you like receive from your work with Appen?',
        answers=['Gaming credits'],
        question_type='radio_btn')

    app.ce_profile.more_about_me.answer_question(
        question='What type of workspace do you use when working for Appen?',
        answers=['Home-office'],
        question_type='radio_btn'
    )

    app.ce_profile.more_about_me.answer_question(
        question='How much time do you believe you spend per month in your home-office workspace when working for Appen?',
        answers=['50-100 hours per month'],
        question_type='radio_btn',
        action='Save Changes'
    )

    appen_work = app.ce_profile.more_about_me.get_progress_for_category('Appen Work')
    assert appen_work == {'questions': '11 questions', 'progress': '100%'}


def test_ce_profile_entertainment_category(app, new_ce_account):
    """
    verify user is able to change answers
    """

    app.ce_profile.open_tab('MORE ABOUT ME')
    app.ce_profile.more_about_me.click_edit_answers_for_category('Entertainment & Activities')

    questions = app.ce_profile.more_about_me.get_all_questions_for_category()
    print(questions)

    app.ce_profile.more_about_me.answer_question(
        question='Do you like to read books?',
        answers=['No'],
        question_type='radio_btn',
        action='Save Changes'
    )

    progress = app.ce_profile.more_about_me.get_progress_for_category('Entertainment & Activities')
    assert progress == {'questions': '2 questions', 'progress': '50%'}

    app.ce_profile.more_about_me.click_edit_answers_for_category('Entertainment & Activities')
    app.ce_profile.more_about_me.answer_question(
        question='Do you pay for any streaming services?',
        answers=['No'],
        question_type='radio_btn',
        action='Save Changes'
    )

    progress = app.ce_profile.more_about_me.get_progress_for_category('Entertainment & Activities')
    assert progress == {'questions': '2 questions', 'progress': '100%'}

    # edit answers
    app.ce_profile.more_about_me.click_edit_answers_for_category('Entertainment & Activities')

    app.ce_profile.more_about_me.answer_question(
        question='Do you like to read books?',
        answers=['Yes'],
        question_type='radio_btn'
    )

    app.ce_profile.more_about_me.answer_question(
        question='How many books would you read annually?',
        answers=['11-15 books'],
        question_type='radio_btn'
    )

    app.ce_profile.more_about_me.answer_question(
        question='What type of books do you like to read?',
        answers=['Action & adventure', 'Comic'],
        question_type='checkbox'
    )

    app.ce_profile.more_about_me.answer_question(
        question='Do you pay for any streaming services?',
        answers=['Yes'],
        question_type='radio_btn'
    )

    app.ce_profile.more_about_me.answer_question(
        question='Which streaming service do you have at home?',
        answers=['Amazon Prime Video', 'Hulu', 'Foxtel', 'Other, please specify'],
        question_type='checkbox'
    )

    app.ce_profile.more_about_me.answer_question(
        question="Please specify which \'other\' streaming service you pay for",
        answers='test',
        question_type='input_field',
        action='Save Changes'
    )

    progress = app.ce_profile.more_about_me.get_progress_for_category('Entertainment & Activities')
    assert progress == {'questions': '5 questions', 'progress': '100%'}


def test_ce_profile_environmental_category(app, new_ce_account):
    app.ce_profile.open_tab('MORE ABOUT ME')
    app.ce_profile.more_about_me.click_edit_answers_for_category('Environmental')

    questions = app.ce_profile.more_about_me.get_all_questions_for_category()
    assert questions == ['HOW AWARE/ EDUCATED DO YOU BELIEVE YOU ARE ON THE WAYS TO REDUCE YOUR CARBON EMISSIONS TO TACKLE CLIMATE CHANGE?',
                         'HOW INVOLVED ARE YOU WHEN IT COMES TO TAKING ACTION TO REDUCE YOUR EMISSIONS AS AN INDIVIDUAL?',
                         'DO YOU PARTICIPATE IN ANY OF THE FOLLOWING RECYCLING INITIATIVES?',
                         'HOW IS YOUR HEATING MAINLY GENERATED WITHIN YOUR HOME?',
                         'HOW IS YOUR COOLING MAINLY GENERATED WITHIN YOUR HOME?',
                         'HOW MANY LIGHT BULBS WOULD YOU USE IN YOUR HOME ON AVERAGE THROUGHOUT THE DAY?',
                         'WHAT PERCENTAGE OF YOUR HOME ELECTRICITY COMES FROM RENEWABLE SOURCES?']

    app.ce_profile.more_about_me.answer_question(
        question='How aware/ educated do you believe you are on the ways to reduce your carbon emissions to tackle climate change?',
        answers=['Very aware'],
        question_type='radio_btn'
    )

    app.ce_profile.more_about_me.answer_question(
        question='How involved are you when it comes to taking action to reduce your emissions as an individual?',
        answers=['Acting on multiple fronts'],
        question_type='radio_btn'
    )

    app.ce_profile.more_about_me.answer_question(
        question='Do you participate in any of the following recycling initiatives?',
        answers=['Cosmetics'],
        question_type='radio_btn'
    )

    app.ce_profile.more_about_me.answer_question(
        question='How is your heating mainly generated within your home?',
        answers=['Electric'],
        question_type='radio_btn'
    )

    app.ce_profile.more_about_me.answer_question(
        question='How is your cooling mainly generated within your home?',
        answers=['Solar powered'],
        question_type='radio_btn'
    )

    app.ce_profile.more_about_me.answer_question(
        question='How many light bulbs would you use in your home on average throughout the day?',
        answers=['2'],
        question_type='radio_btn'
    )

    app.ce_profile.more_about_me.answer_question(
        question='What percentage of your home electricity comes from renewable sources?',
        answers=['20%-40%'],
        question_type='radio_btn',
        action='Save Changes'
    )

    progress = app.ce_profile.more_about_me.get_progress_for_category('Environmental')
    assert progress == {'questions': '8 questions', 'progress': '87%'}


def test_ce_profile_family_category(app, new_ce_account):
    app.ce_profile.open_tab('MORE ABOUT ME')
    app.ce_profile.more_about_me.click_edit_answers_for_category('Family & Me')

    questions = app.ce_profile.more_about_me.get_all_questions_for_category()
    print(questions)

    app.ce_profile.more_about_me.answer_question(
        question='Which gender do you identify with?',
        answers=['Man'],
        question_type='radio_btn'
    )
    # TODO DOB

    app.ce_profile.more_about_me.answer_question(
        question='In which country were you born?',
        answers='United States of America',
        question_type='dropdown'
    )

    app.ce_profile.more_about_me.answer_question(
        question='In which city were you born?',
        answers='Boston',
        question_type='input_field'
    )

    app.ce_profile.more_about_me.answer_question(
        question='What is your current religion practice?',
        answers=['I prefer not to say'],
        question_type='radio_btn'
    )

    app.ce_profile.more_about_me.answer_question(
        question='Do you have any children?',
        answers=['No'],
        question_type='radio_btn',
        action='Save Changes'
    )

    progress = app.ce_profile.more_about_me.get_progress_for_category('Family & Me')
    print(progress)
    # assert progress == {'questions': '5 questions', 'progress': '100%'}


def test_ce_profile_health_category(app, new_ce_account):
    app.ce_profile.open_tab('MORE ABOUT ME')
    app.ce_profile.more_about_me.click_edit_answers_for_category('Health & Medical')

    questions = app.ce_profile.more_about_me.get_all_questions_for_category()
    assert questions == ['DO YOU HAVE ANY OF THE FOLLOWING SPEECH OR VISION IMPAIRMENTS? (PLEASE SELECT ALL THAT APPLY) (OPTIONAL)',
                         'DO YOU HAVE DIFFICULTY SEEING, EVEN IF WEARING GLASSES?',
                         'DO YOU HAVE DIFFICULTY HEARING, EVEN IF USING A HEARING AID(S)?',
                         'DO YOU HAVE DIFFICULTY WALKING OR CLIMBING STEPS?',
                         'DO YOU HAVE DIFFICULTY REMEMBERING OR CONCENTRATING?',
                         'DO YOU HAVE DIFFICULTY WITH SELF-CARE, SUCH AS WASHING ALL OVER OR DRESSING?',
                         'USING YOUR USUAL LANGUAGE, DO YOU HAVE DIFFICULTY COMMUNICATING, FOR EXAMPLE UNDERSTANDING OR BEING UNDERSTOOD?']

    app.ce_profile.more_about_me.answer_question(
        question='Do you have any of the following speech or vision impairments? (please select all that apply)',
        answers=['Blurred Vision', 'Lisp'],
        question_type='checkbox'
    )

    app.ce_profile.more_about_me.answer_question(
        question='Do you have difficulty seeing, even if wearing glasses?',
        answers=['No difficulty'],
        question_type='radio_btn',
        action='Save Changes'
    )

    progress = app.ce_profile.more_about_me.get_progress_for_category('Health & Medical')
    assert progress == {'questions': '7 questions', 'progress': '28%'}


def test_ce_profile_home_category(app, new_ce_account):
    app.ce_profile.open_tab('MORE ABOUT ME')
    app.ce_profile.more_about_me.click_edit_answers_for_category('Home & Income')

    questions = app.ce_profile.more_about_me.get_all_questions_for_category()
    assert questions == ['WHAT IS YOUR CURRENT HOME OWNERSHIP STATUS?',
                         'HOW MANY PEOPLE ARE CURRENTLY LIVING IN YOUR HOME (INCLUDING YOURSELF)?',
                         'WHAT IS YOUR HOUSEHOLD INCOME? (PLEASE INDICATE IN USD PER MONTH)',
                         'WHAT IS YOUR PERSONAL INCOME? (PLEASE INDICATE IN USD PER MONTH)',
                         'WHAT TYPE OF RESIDENCE DO YOU CLASSIFY YOUR HOME AS?',
                         'HOW MANY PEOPLE LIVING IN YOUR HOME ARE 18+ YEARS (INCLUDING YOURSELF)?']

    app.ce_profile.more_about_me.answer_question(
        question='What is your current home ownership status?',
        answers=['Renting'],
        question_type='radio_btn'
    )

    app.ce_profile.more_about_me.answer_question(
        question='How many people are currently living in your home (including yourself)?',
        answers=['2 people'],
        question_type='radio_btn',
        action='Save Changes'
    )

    progress = app.ce_profile.more_about_me.get_progress_for_category('Home & Income')
    assert progress == {'questions': '6 questions', 'progress': '33%'}


def test_ce_profile_politics_category(app, new_ce_account):
    app.ce_profile.open_tab('MORE ABOUT ME')
    app.ce_profile.more_about_me.click_edit_answers_for_category('Politics')

    questions = app.ce_profile.more_about_me.get_all_questions_for_category()
    assert questions == ['HOW ENGAGED ARE YOU IN POLITICS IN THE COUNTRY IN WHICH YOU LIVE?']

    app.ce_profile.more_about_me.answer_question(
        question='How engaged are you in politics in the country in which you live?',
        answers=['Frequent engagement'],
        question_type='radio_btn',
        action='Save Changes'
    )

    progress = app.ce_profile.more_about_me.get_progress_for_category('Politics')
    assert progress == {'questions': '1 question', 'progress': '100%'}

def test_ce_profile_social_category(app, new_ce_account):
    app.ce_profile.open_tab('MORE ABOUT ME')
    app.ce_profile.more_about_me.click_edit_answers_for_category('Social')

    questions = app.ce_profile.more_about_me.get_all_questions_for_category()
    assert questions == ['DO YOU USE ANY SOCIAL APPS / MESSENGER ACCOUNTS?']

    app.ce_profile.more_about_me.answer_question(
        question='Do you use any social apps / messenger accounts?',
        answers=['Yes'],
        question_type='radio_btn'
    )

    app.ce_profile.more_about_me.answer_question(
        question='Which of the following social apps/ messenger accounts do you have?',
        answers=['Facebook'],
        question_type='radio_btn'
    )

    app.ce_profile.more_about_me.answer_question(
        question='How often are you interacting on Facebook?',
        answers=['Daily'],
        question_type='radio_btn'
    )

    app.ce_profile.more_about_me.answer_question(
        question='How long have you had your Facebook account?',
        answers=['12-24 months'],
        question_type='radio_btn'
    )

    app.ce_profile.more_about_me.answer_question(
        question='How many friends do you have on Facebook?',
        answers=['51-75 friends'],
        question_type='radio_btn',
        action='Save Changes'
    )

    progress = app.ce_profile.more_about_me.get_progress_for_category('Social')
    assert progress == {'questions': '5 questions', 'progress': '100%'}


def test_ce_profile_technologies_category(app, new_ce_account):
    app.ce_profile.open_tab('MORE ABOUT ME')
    app.ce_profile.more_about_me.click_edit_answers_for_category('Technologies & Communications')

    questions = app.ce_profile.more_about_me.get_all_questions_for_category()
    assert questions ==['WHAT BRAND OF TABLET DEVICE DO YOU OWN OR HAVE ACCESS TO?',
                         'WHAT MODEL(S) OF TABLET DO YOU OWN?',
                         'WHAT TYPE OF MOBILE OPERATING SYSTEM DO YOU OWN OR HAVE ACCESS TO?',
                         'WHAT BRAND OF MOBILE DEVICE DO YOU CURRENTLY OWN OR HAVE ACCESS TO?',
                         'WHAT VERSION OF MOBILE DEVICE DO YOU OWN OR HAVE ACCESS TO?',
                         "DO YOU USE YOUR MOBILE DEVICE'S VOICE ASSISTANT?",
                         'DO YOU OWN OR HAVE ACCESS TO BLUETOOTH?',
                         'DO YOU OWN OR HAVE ACCESS TO ANY OF THE FOLLOWING HEADSET DEVICES?',
                         'DO YOU OWN OR HAVE ACCESS TO A WEBCAM?',
                         'DO YOU OWN A GAMING DEVICE? (E.G. XBOX, NINTENDO, PLAYSTATION ETC.)',
                         'DO YOU OWN A VR (VIRTUAL REALITY) HEADSET?',
                         'DO YOU OWN AR (AUGMENTED REALITY) GLASSES?',
                         'DO YOU HAVE ACCESS TO ANY OF THE BELOW NON-MOBILE TELEPHONY SERVICES (E.G. '
                         'HOME LANDLINE, OFFICE PBX)?',
                         'WHICH CAMERA EQUIPMENT DO YOU OWN OR HAVE ACCESS TO?',
                         'DO YOU OWN A SMART HOME SPEAKER (E.G. GOOGLE HOME, AMAZON ECHO ETC.)?',
                         'DO YOU OWN A LAPTOP OR DESKTOP DEVICE?',
                         "PLEASE SPECIFY 'OTHER' BRAND OF MOBILE DEVICE"]

    app.ce_profile.more_about_me.answer_question(
        question='What brand of tablet device do you own or have access to?',
        answers=['Amazon', 'Apple', 'Huawei'],
        question_type='checkbox'
    )

    app.ce_profile.more_about_me.answer_question(
        question='What type of mobile operating system do you own or have access to?',
        answers=['Android', 'Apple iOS', 'Palm'],
        question_type='checkbox'
    )

    app.ce_profile.more_about_me.answer_question(
        question='Do you own or have access to bluetooth?',
        answers=['Yes'],
        question_type='radio_btn',
        action='Save Changes'
    )

    progress = app.ce_profile.more_about_me.get_progress_for_category('Technologies & Communications')
    assert  progress == {'questions': '17 questions', 'progress': '17%'}


def test_ce_profile_transport_category(app, new_ce_account):
    app.ce_profile.open_tab('MORE ABOUT ME')
    app.ce_profile.more_about_me.click_edit_answers_for_category('Transport')

    questions = app.ce_profile.more_about_me.get_all_questions_for_category()
    assert questions == ['DO YOU OWN ANY MODE OF TRANSPORTATION?']

    app.ce_profile.more_about_me.answer_question(
        question='Do you own any mode of transportation?',
        answers=['No'],
        question_type='radio_btn',
        action='Save Changes'
    )

    progress = app.ce_profile.more_about_me.get_progress_for_category('Transport')
    assert progress == {'questions': '1 question', 'progress': '100%'}


def test_ce_profile_work_and_education_category(app, new_ce_account):
    app.ce_profile.open_tab('MORE ABOUT ME')
    app.ce_profile.more_about_me.click_edit_answers_for_category('Work & Education')

    questions = app.ce_profile.more_about_me.get_all_questions_for_category()
    assert questions == ['DO YOU HAVE A LINGUISTICS DEGREE OR ARE CURRENTLY STUDYING LINGUISTICS?',
                         'WHAT IS THE HIGHEST LEVEL OF EDUCATION YOU HAVE ACHIEVED?',
                         'WHAT IS YOUR CURRENT WORKING STATUS?',
                         'DO YOU HAVE EXPERIENCE IN ANY OF THE FOLLOWING AREAS?',
                         'ARE YOU CURRENTLY WORKING AS A SEARCH ENGINE EVALUATOR?']

    app.ce_profile.more_about_me.answer_question(
        question='Do you have a linguistics degree or are currently studying linguistics?',
        answers=['Professional Certificate - Currently studying'],
        question_type='radio_btn'
    )

    app.ce_profile.more_about_me.answer_question(
        question='What is the highest level of education you have achieved?',
        answers=['Doctorate degree or equivalent'],
        question_type='radio_btn'
    )

    app.ce_profile.more_about_me.answer_question(
        question='What is your current working status?',
        answers=['Self-employed'],
        question_type='radio_btn'
    )

    app.ce_profile.more_about_me.answer_question(
        question='What industry do you work in?',
        answers=['Automotive'],
        question_type='radio_btn'
    )

    app.ce_profile.more_about_me.answer_question(
        question='Do you have experience in any of the following areas? ',
        answers=['Proofreading', 'Automated speech recognition – engine development', 'Phonetics'],
        question_type='checkbox'
    )

    app.ce_profile.more_about_me.answer_question(
        question='Are you currently working as a search engine evaluator?',
        answers=['Yes'],
        question_type='radio_btn'
    )

    app.ce_profile.more_about_me.answer_question(
        question='Please specify the company (or companies) for which you are currently working as a search engine evaluator?',
        answers='Test',
        question_type='input_field',
        action='Save Changes'
    )

    progress = app.ce_profile.more_about_me.get_progress_for_category('Work & Education')
    assert progress == {'questions': '7 questions', 'progress': '100%'}




