import time
import datetime
import datetime as ds
from adap.api_automation.utils.data_util import *
from appen_connect.api_automation.services_config.ac_user_service import UserService

USER_NAME = get_test_data('vendor_profile', 'email')
PASSWORD = get_test_data('vendor_profile', 'password')
ID = get_test_data('vendor_profile', 'id')

pytestmark = [pytest.mark.regression_ac_vendor_profile,
              pytest.mark.regression_ac,
              pytest.mark.ac_ui_vendor_registration]


@pytest.fixture(scope="module")
def login(app):
    app.ac_user.login_as(user_name=USER_NAME, password=PASSWORD)
    cookie_dict = {seleniumCookie['name']: seleniumCookie['value'] for seleniumCookie in app.driver.get_cookies()}

    url = {
        "stage": "https://connect-stage.integration.cf3.us/qrp/core/vendors/user_profile_setup?test=true",
        "qa": "https://connect-qa.sandbox.cf3.us/qrp/core/vendors/user_profile_setup?test=true",
    }

    app.driver.get(url[pytest.env])
    time.sleep(3)
    app.navigation.switch_to_frame("page-wrapper")

    global _vendor_profile, _education_levels, _linguistics_qualification

    _vendor_profile = {}
    payload_file = get_data_file('/vendor_profile.json')
    with open(payload_file, "r") as read_file:
        _vendor_profile = json.load(read_file)

    api = UserService()
    if _vendor_profile != {}:
        res = api.update_vendor_profile(ID, _vendor_profile, cookie_dict)
        assert res.status_code == 200

    res = api.get_vendor_profile(ID, cookie_dict)
    print("profile:", res.json_response)

    _education_levels = api.get_education_levels(cookies=cookie_dict).json_response
    _linguistics_qualification = api.get_linguistics_qualification(cookies=cookie_dict).json_response

    yield

    if _vendor_profile != {}:
        res = api.update_vendor_profile(ID, _vendor_profile, cookie_dict)
        assert res.status_code == 200


# def test_temp(app):
#     app.ac_user.login_as(user_name=USER_NAME, password=PASSWORD)
#     cookie_dict = {seleniumCookie['name']: seleniumCookie['value'] for seleniumCookie in app.driver.get_cookies()}
#
#     url = {
#         "stage": "https://connect-stage.integration.cf3.us/qrp/core/vendors/user_profile_setup?test=true",
#         "qa": "https://connect-qa.sandbox.cf3.us/qrp/core/vendors/user_profile_setup?test=true",
#     }
#
#     app.driver.get(url[pytest.env])
#     time.sleep(3)
#     app.navigation.switch_to_frame("page-wrapper")
#     api = UserService()
#
#     res = api.get_vendor_profile(ID, cookie_dict)
#     print("profile:", res.json_response)


def test_main_page_vendor_profile(app, login):
    app.verification.text_present_on_page("Basic Information")
    app.verification.text_present_on_page("Languages")
    app.verification.text_present_on_page("Location")
    app.verification.text_present_on_page("Education")
    app.verification.text_present_on_page("Work Experience")
    app.verification.text_present_on_page("Phone Number")
    app.verification.text_present_on_page("Preview")


@pytest.mark.dependency()
def test_basic_information_vendor_profile(app, login):
    app.vendor_profile.open_tab('Basic Information')

    app.verification.text_present_on_page("Choose your contract type to proceed")

    app.verification.text_present_on_page("Work Experience")
    app.verification.text_present_on_page("Phone Number")
    app.verification.text_present_on_page("Preview")
    app.vendor_profile.basic_information.set_up_contract_type('Business Contractor')

    BUSINESS_NAME = get_test_data('vendor_profile', 'full_name')
    vendor_info = app.vendor_profile.get_information_from_page()
    assert vendor_info['BUSINESS NAME'] == BUSINESS_NAME
    assert vendor_info['FIRST NAME'] == get_test_data('vendor_profile', 'first_name')
    assert vendor_info['LAST NAME'] == get_test_data('vendor_profile', 'last_name')

    # verify required fields
    app.vendor_profile.basic_information.remove_data({"BUSINESS NAME": BUSINESS_NAME})
    app.vendor_profile.click_out("Business Name")
    app.verification.text_present_on_page("Required field")

    # Edit Business Contractor Name
    app.vendor_profile.basic_information.fill_out_fields({"BUSINESS NAME": BUSINESS_NAME + "Test"})
    app.vendor_profile.click_out("Business Name")
    app.navigation.click_btn("Next: Languages")
    app.navigation.click_btn("Back")

    # Verify Edited Business Contractor remain in the page after return
    vendor_info = app.vendor_profile.get_information_from_page()
    assert vendor_info['BUSINESS NAME'] == BUSINESS_NAME + "Test"

    app.vendor_profile.basic_information.set_up_contract_type("Independent Contractor")
    vendor_info = app.vendor_profile.get_information_from_page()
    assert not vendor_info.get('BUSINESS NAME')

    app.vendor_profile.basic_information.set_up_contract_type("Business Contractor")

    app.navigation.click_btn("Next: Languages")


# @pytest.mark.skip(reason='deprecated')
# def test_demographic_consent_decline(app, login):
#     app.vendor_profile.open_tab('Basic Information')
#
#     app.verification.text_present_on_page("Demographics")
#     app.verification.text_present_on_page("By answering the questions bellow you will see targeted job opportunities on your project list. Tick to unlock the form.")
#
#     app.vendor_profile.basic_information.fill_out_fields({
#         "DEMOGRAPHIC CONSENT": "1"})
#
#     app.verification.text_present_on_page("Informed Consent Form for Appen Crowd Research")
#     app.verification.text_present_on_page("In this Informed Consent Form (“ICF”), you are agreeing to assist Appen in a data collection activity or series of activities undertaken by Appen (“Activity” or “Project”). For the purposes of the Activity, Appen will collect data for its own internal use. Appen is the data controller.")
#     app.verification.text_present_on_page(
#         "Your decision to participate in the Activity is completely voluntary and you may decline to participate or request to end your participation in the Activity at any time. You acknowledge that no payment shall be provided to you for your participation.")
#     app.verification.text_present_on_page(
#         "By providing your signature below, you are agreeing to provide Appen Butler Hill Pty Ltd, with address at Level 6, 9 Help Street Chatswood, NSW 2067 Australia, (or its affiliates) (“Appen”, “us”, “we”, “our”) with personal data, including but not limited to, physical characteristics, location, work or life experiences, opinions, health, socioeconomic status, biometric data, sexuality, family or relationship status for the Activity (we call this “Activity Data”), and any other information and materials that you provide to us as required under the Activity (which, together with the Activity Data will be referred to as “Materials”). By way of example only, the Materials may include personal data pertaining to age, gender, race, ethnicity, sex, sexuality, political affiliation or opinions, religious or philosophical beliefs, trade union membership, health data, criminal background, voice data, facial/body images or videos; or data concerning a person’s sex life or sexual orientation. The Materials will be used by Appen as well as our vendors who sub process the Materials (each, a “User” and collectively, the “Users”) to assist in better understanding the demographics of our crowd and to offer you and those members more relevant opportunities. Your assistance is much appreciated. For more information on how Appen uses data, please review Appen’s Privacy Statement located on our website at:")
#     app.verification.text_present_on_page("Processing of Personal Information")
#     app.verification.text_present_on_page(
#         "We may need to collect, use, and retain personal data from you, or from another entity you provide your personal data to, in order to: execute the Activity requirements; communicate with you and fulfill any other obligations we may have to our customers, vendors, or to regulatory authorities. If you wish to withdraw your participation, please contact Appen at the Appen Contact email below. After your withdrawal, Appen may continue to use the Activity Data that you provided but only in accordance with applicable law and our legitimate business interests. For instance, Appen and Users may continue to retain your account information, such as what Activities or Projects you participated in, for account management and record-keeping purposes.")
#     app.verification.text_present_on_page("Ownership and Use of Materials.")
#     app.verification.text_present_on_page("The Materials shall be deemed works made for hire for Appen. Accordingly, Appen shall be considered the author and the owner of the Materials at all stages of completion. All rights (the “Rights”), including but not limited to, all copyrights, and any and all ownership and exploitation rights, in the Materials and the images, video, audio, and other content contained therein, in whatever form in which you appear, are hereby assigned to Appen to be used for the benefit of Appen and its customers throughout the world in all forms of media, forever. If under any applicable law the fact that the Materials are a work made for hire is not effective to place authorship and ownership of the Materials and all rights therein in Appen, then you hereby irrevocably assign, transfer, and/or release such rights to Appen and in favor of Appen to the fullest extent permitted by applicable law, and in connection therewith, any and all right, title and interest you may have in the Materials. Depending on the Project description, you may be asked to submit Materials of other individual persons besides yourself. You understand and agree that you will obtain all necessary and valid consents and/or acknowledgments from additional participants before you submit the Materials of other individual persons. The method by which others may register their consent or acknowledgments is specified in the Project guidelines and you will strictly comply with any instructions requiring your assistance or cooperation. You hereby represent, warrant, and covenant that you have or will obtain all consents, acknowledgments, and assignments as required to provide Appen and the Users with rights necessary to collect, use, store, process, transfer, and disclose of each of those individuals’ personal data as described in this Informed Consent Form, including but not limited to, assignment of all of their intellectual property and waiver of moral rights as needed in accordance with this ICF.")
#     app.verification.text_present_on_page("Release of Claims (PLEASE READ CAREFULLY)")
#     app.verification.text_present_on_page("TO THE FULLEST EXTENT PERMITTED BY APPLICABLE LAW, YOU, ON BEHALF OF YOURSELF, AND ANY OTHER APPLICABLE INDIVIDUALS, EACH HEREBY WAIVE, RELEASE, DISCHARGE, AND HOLD APPEN, APPEN'S CUSTOMER, AND ANY OTHER USERS HARMLESS FROM LIABILITY BY VIRTUE OF ANY PROCESSING, BLURRING, DISTORTION, ALTERATION, ANNOTATION, MODIFICATION, OPTICAL ILLUSION, OR USE OF THE MATERIALS OR OTHER CONTENT IN COMPOSITE FORM WHETHER INTENTIONAL OR OTHERWISE, THAT MAY OCCUR OR BE PRODUCED WHEN WE, APPEN, OR OTHER USERS USE THE MATERIALS, INCLUDING BUT NOT LIMITED TO ANY CLAIMS FOR INVASION OF PRIVACY, DEFAMATION, AND VIOLATION OF PUBLICITY OR PERSONALITY RIGHTS. YOU UNDERSTAND THAT SUCH ALTERATIONS ARE AN EXPRESS AND INTENDED USE OF THE MATERIALS.")
#
#     app.verification.text_present_on_page("Limitation of Liability.")
#     app.verification.text_present_on_page("TO THE MAXIMUM EXTENT PERMITTED UNDER APPLICABLE LAW, IN NO EVENT WILL APPEN, ITS CUSTOMER, OR OTHER USERS, BE LIABLE TO YOU OR ANY OTHER INDIVIDUAL PARTICIPATING IN THIS PROJECT FOR ANY INDIRECT, SPECIAL, EXEMPLARY, INCIDENTAL, OR CONSEQUENTIAL DAMAGES (INCLUDING LOSS OF PROFITS OR LOSS OF TIME) ARISING FROM OR RELATING TO THIS AGREEMENT, EVEN IF APPEN, CUSTOMER, OR OTHER USERS KNEW OR SHOULD HAVE KNOWN OF THE POSSIBILITY OF, OR COULD REASONABLY HAVE PREVENTED, SUCH DAMAGES. UNDER NO CIRCUMSTANCES WILL APPEN, APPEN'S CUSTOMER, OR USERS’ TOTAL AGGREGATE LIABILITY OF ALL KINDS ARISING OUT OF OR RELATED TO THIS PROJECT EXCEED THE TOTAL AMOUNT PAID BY APPEN TO YOU UNDER THIS PROJECT DURING THE TWELVE MONTHS IMMEDIATELY PRECEDING THE CLAIM. SOME JURISDICTIONS DO NOT ALLOW THE EXCLUSION OR LIMITATION OF LIABILITY FOR CONSEQUENTIAL OR INCIDENTAL DAMAGES; THUS, THE ABOVE LIMITATION MAY NOT APPLY IN SUCH JURISDICTIONS.")
#     app.verification.text_present_on_page("Data Transfer")
#     app.verification.text_present_on_page("You acknowledge and agree that Activity Data may be transferred to Appen, to Users, to the United States, Canada, the United Kingdom, the European Union, Australia, Philippines, and other countries, but only for the purposes described herein. The transfer of personal data to these entities will abide by the requirements for international data transfers per applicable law. These entities will subscribe to the appropriate legal instruments for the international transfer of data, or will be bound by appropriate contractual arrangements (such as Standard Contractual Clauses, as approved by the European Commission) to protect your personal information.")
#     app.verification.text_present_on_page("Your Rights in Activity Data")
#     app.verification.text_present_on_page("You agree that the Activity Data submitted by you are original to and owned by you, or the other data subject(s). By submitting, you release, to the maximum extent permitted by law, Appen, Users, agents, employees, licensees and assigns from any and all claims you may have now or in the future for invasion of privacy, right of publicity, trademark infringement, copyright infringement, defamation or any other cause of action arising out of Appen’s use of the Activity Data submitted by you. You understand and agree that between Appen and you, Appen is and shall be the exclusive owner of all right, title and interest, including copyright, in the Activity Data and any works that may be created containing the Activity Data.")
#     app.verification.text_present_on_page("Withdrawal and Questions")
#     app.verification.text_present_on_page("If you have any questions or would like to withdraw your consent, you may contact any of the following: the ")
#     app.verification.text_present_on_page("support@connect-mail.appen.com")
#     app.verification.text_present_on_page(". You may also contact our data protection officer at dpo@appen.com. You may be asked to go through our standard data subject access rights process.")
#
#     app.verification.text_present_on_page("YOU ACKNOWLEDGE THAT YOU HAVE READ THIS INFORMED CONSENT FORM CAREFULLY, THAT YOU UNDERSTAND AND AGREE TO ALL OF ITS TERMS AND HAVE HAD AN OPPORTUNITY TO ASK QUESTIONS.")
#     app.verification.text_present_on_page("You hereby consent to Appen processing your personal information including Activity Data as follows:")
#     app.verification.text_present_on_page("• Assessing the relevance of certain tasks that we might offer for you to perform.")
#     app.verification.text_present_on_page("You do not have to give us your consent and withholding your consent will not by itself affect your eligibility to register as a crowd member for us, although we may be less likely to engage you to perform certain tasks that require access to Activity Data and you may not have as many opportunities for work. You can also withdraw your consent at any time by logging on to your crowd account on our website/platforms.")
#     app.verification.text_present_on_page("You understand that you may ask for a copy of this Informed Consent Form. Facsimile signatures constitute original signatures for all purposes.")
#
#     app.navigation.click_btn("Decline")
#
#
# @pytest.mark.skip(reason='deprecated')
# def test_demographic_information_accept(app, login):
#     app.vendor_profile.open_tab('Basic Information')
#
#     app.vendor_profile.basic_information.fill_out_fields({
#         "DEMOGRAPHIC CONSENT": "1"})
#
#     app.navigation.click_btn("Accept")
#
#     app.verification.text_present_on_page("You are considered to have a disability if you have a physical or mental impairment or medical condition that substantially limits a major life activity, or if you have a history or record of such an impairment or medical condition.")
#     app.verification.text_present_on_page("Disabilities include, but are not limited to:")
#     app.verification.text_present_on_page("Autism")
#     app.verification.text_present_on_page("Bipolar disorder")
#     app.verification.text_present_on_page("Blindness")
#     app.verification.text_present_on_page("Cancer")
#     app.verification.text_present_on_page("Cerebral palsy")
#     app.verification.text_present_on_page("Deafness")
#     app.verification.text_present_on_page("Diabetes")
#     app.verification.text_present_on_page("Epilepsy")
#     app.verification.text_present_on_page("HIV/AIDS")
#     app.verification.text_present_on_page("Impairments requiring the use of a wheelchair")
#     app.verification.text_present_on_page("Intellectual disability")
#     app.verification.text_present_on_page("Major depression")
#     app.verification.text_present_on_page("Missing limbs or partially missing limbs")
#     app.verification.text_present_on_page("Multiple sclerosis (MS)")
#     app.verification.text_present_on_page("Muscular dystrophy")
#     app.verification.text_present_on_page("Obsessive compulsive disorder")
#     app.verification.text_present_on_page("Post-traumatic stress disorder (PTSD)")
#     app.verification.text_present_on_page("Schizophrenia")
#
#     datetime.date.today().strftime("%m/%d/%Y")
#     birth_date = (datetime.date.today() - datetime.timedelta(days=18000)).strftime("%m/%d/%Y")
#     formatted_date = (custom_strftime('%b %d, %Y', (datetime.date.today() - datetime.timedelta(days=18000))))
#
#     app.vendor_profile.basic_information.fill_out_fields(
#         {
#             "DATE OF BIRTH": birth_date
#         })
#     app.navigation.click_btn("Next: Languages")
#     app.navigation.click_btn("Back")
#     vendor_info = app.vendor_profile.get_information_from_page()
#
#     assert vendor_info['DATE OF BIRTH'] == formatted_date
#
#     app.vendor_profile.open_tab('Preview')
#     vendor_info = app.vendor_profile.get_information_from_page()
#
#     assert vendor_info['DATE OF BIRTH'] == formatted_date
#     assert vendor_info['COMPLEXION'] == ""
#     assert vendor_info['ETHNICITY'] == ""
#     assert vendor_info['GENDER YOU IDENTIFY WITH'] == ""
#     assert vendor_info['ARE YOU CONSIDERED DISABLED?'] == ""
#
#
# @pytest.mark.parametrize("complexion, ethnicity, gender, disability", [
#     ("Type 1: Light - pale white", "Black or African American", "Female", "Yes - I have a disability"),
#     ("Type 2: White - fair", "Hispanic or Latin American", "Male", "No - I don’t have a disability"),
#     ("Type 3: Median - white to light brown", "American Indian or Alaska Native", "Non-Binary / Other",
#      "I don’t wish to answer")
# ])
# @pytest.mark.dependency(depends=["test_demographic_information_accept"])
# def test_input_demographic_information(app, login, complexion, ethnicity, gender, disability):
#     app.vendor_profile.open_tab('Basic Information')
#
#     app.vendor_profile.basic_information.fill_out_fields(
#         {
#             "COMPLEXION": complexion,
#             "ETHNICITY": ethnicity,
#             "GENDER YOU IDENTIFY WITH": gender,
#             "ARE YOU CONSIDERED DISABLED?": disability
#         })
#
#     app.navigation.click_btn("Next: Languages")
#     app.navigation.click_btn("Back")
#
#     vendor_info = app.vendor_profile.get_information_from_page()
#
#     assert vendor_info['COMPLEXION'] == complexion
#     assert vendor_info['ETHNICITY'] == ethnicity
#     assert vendor_info['GENDER YOU IDENTIFY WITH'] == gender
#     assert vendor_info['ARE YOU CONSIDERED DISABLED?'] == disability
#
#     app.vendor_profile.open_tab('Preview')
#     vendor_info = app.vendor_profile.get_information_from_page()
#
#     assert vendor_info['COMPLEXION'] == complexion
#     assert vendor_info['ETHNICITY'] == ethnicity
#     assert vendor_info['GENDER YOU IDENTIFY WITH'] == gender
#     assert vendor_info['ARE YOU CONSIDERED DISABLED?'] == disability

@pytest.mark.dependency()
def test_languages_vendor_profile(app, login):
    app.vendor_profile.open_tab('Languages')

    app.verification.text_present_on_page("STEP 02")
    app.verification.text_present_on_page("Select your native language and add other languages that you speak")
    # need update xpath
    # app.vendor_profile.languages.verify_data({
    #     "YOUR PRIMARY LANGUAGE": "English",
    #     "YOUR LANGUAGE REGION":  "United States of America"
    # })

    app.vendor_profile.languages.fill_out_fields({
        "Additional languages": "1"
    })
    # Verify Required Fields on Add Additional Languagues and Add Values
    app.navigation.click_btn("Add Additional Language")
    app.vendor_profile.click_drop('LOCALE LANGUAGE')
    app.vendor_profile.click_drop('LANGUAGE REGION')
    app.vendor_profile.languages.add_additional_language({"LOCALE LANGUAGE": "Russian"})
    app.vendor_profile.languages.add_additional_language({"LANGUAGE REGION": "Ukraine"})
    app.vendor_profile.click_drop('SPOKEN FLUENCY')
    app.vendor_profile.click_drop('WRITTEN FLUENCY')
    app.vendor_profile.languages.add_additional_language({"SPOKEN FLUENCY": "Advanced"})
    app.vendor_profile.languages.add_additional_language({"WRITTEN FLUENCY": "Advanced"})
    app.vendor_profile.languages.add_additional_language({}, action='Save')

    tab_content = app.vendor_profile.get_table_content("Additional languages")
    assert len(tab_content) == 1
    assert tab_content[0]['LOCAL LANGUAGE'] == 'Russian'
    assert tab_content[0]['LANGUAGE REGION'] == 'Ukraine'
    assert tab_content[0]['SPOKEN FLUENCY'] == 'Advanced'
    assert tab_content[0]['WRITTEN FLUENCY'] == 'Advanced'

    # translation experience
    app.verification.text_present_on_page("Translation experience")
    app.vendor_profile.languages.fill_out_fields({
        "Translation experience": "1"
    })

    app.navigation.click_btn("Add Translation Pair")
    # Verify Required Fields on Translation Pair and Add Values
    app.vendor_profile.click_drop('FROM')
    app.vendor_profile.click_drop('TO')
    app.vendor_profile.languages.add_additional_language({"FROM": "Russian (Ukraine)"})
    app.vendor_profile.languages.add_additional_language({"TO": "English (United States of America)"})
    app.vendor_profile.languages.add_additional_language({}, action='Save')

    translation_content = app.vendor_profile.get_table_content("Translation experience")

    assert translation_content[0]['TRANSLATION FROM'] == 'Russian (Ukraine)'
    assert translation_content[0]['TO'] == 'English (United States of America)'

    app.navigation.click_btn("Next: Location")
    app.navigation.click_btn("Back")

    tab_content = app.vendor_profile.get_table_content("Additional languages")
    translation_content = app.vendor_profile.get_table_content("Translation experience")

    assert len(tab_content) == 1
    assert len(translation_content) == 1

    app.navigation.click_btn("Next: Location")


@pytest.mark.dependency()
def test_location_vendor_profile(app, login):
    app.vendor_profile.open_tab('Location')

    app.verification.text_present_on_page("STEP 03")
    # residency_history_date = (ds.date.today() - ds.timedelta(days=1800)).strftime("%Y/%m/%d")
    app.vendor_profile.location.verify_data({
        "Street Address": _vendor_profile['address'],
        "CITY": _vendor_profile['city'],
        "ZIP CODE": _vendor_profile['zip'],
        "Residency History": ""
    }  # _vendor_profile['residencyYears']
    )

    app.verification.text_present_on_page('United States of America')
    app.verification.text_present_on_page('California')

    # Verify Street Address is Required Fields when empty
    ADDRESS = _vendor_profile['address']
    app.vendor_profile.location.remove_data({"Street Address": ADDRESS})
    app.vendor_profile.click_out("Street Address")
    app.verification.text_present_on_page("Required field")
    app.vendor_profile.location.fill_out_fields({"Street Address": "20 Main Street testing"})

    # Verify City is Required Fields when empty
    CITY = _vendor_profile['city']
    app.vendor_profile.location.remove_data({"CITY": CITY})
    app.vendor_profile.click_out("CITY")
    app.verification.text_present_on_page("Required field")
    app.vendor_profile.location.fill_out_fields({"CITY": "San Francisco"})

    # Verify Zip Code is Required Fields when empty
    ZIP = _vendor_profile['zip']
    app.vendor_profile.location.remove_data({"ZIP CODE": ZIP})
    app.vendor_profile.click_out("ZIP CODE")
    app.verification.text_present_on_page("Required field")
    app.vendor_profile.location.fill_out_fields({"ZIP CODE": "G1K2A5"})

    # BUG--> to Verify Years of Residence is Required Fields when empty, feature changed
    # YEARS = _vendor_profile['residencyYears']
    # print('residencyYears: ', YEARS)
    # app.vendor_profile.location.fill_out_fields({"YEARS": "1 year"})
    # time.sleep(2)
    # app.navigation.click_btn("Next: Education")
    # app.navigation.click_btn("Back")
    # time.sleep(2)
    #
    # app.vendor_profile.location.verify_data({
    #     "Street Address": "20 Main Street testing",
    #     "CITY": "San Francisco",
    #     "ZIP CODE": "G1K2A5"
    #     # "YEARS": "1 year"
    # }
    # )

    app.navigation.click_btn("Next: Education")


@pytest.mark.dependency()
def test_education_vendor_profile(app, login):
    app.vendor_profile.open_tab('Education')

    app.verification.text_present_on_page("STEP 04")
    app.verification.text_present_on_page("Enter information about your education level")

    # _current_ed_level = find_dict_in_array_by_value(_education_levels, 'value', _vendor_profile['educationLevel'])['description']
    # _current_ling_qual = find_dict_in_array_by_value(_linguistics_qualification, 'value', _vendor_profile['linguisticQualification'])['label']
    #  need xpath update
    # app.vendor_profile.education.verify_data({
    #     "HIGHEST LEVEL OF EDUCATION": _current_ed_level,
    #     "LINGUISTICS QUALIFICATION": _current_ling_qual}
    # )

    app.vendor_profile.education.fill_out_fields(
        {
            "HIGHEST LEVEL OF EDUCATION": "Doctorate degree or equivalent",
            "LINGUISTICS QUALIFICATION": "Doctoral degree – Completed"
        }
    )

    app.navigation.click_btn("Next: Work Experience")
    app.navigation.click_btn("Back")

    # app.vendor_profile.education.verify_data(
    #     {"HIGHEST LEVEL OF EDUCATION": "Doctorate degree or equivalent",
    #      "LINGUISTICS QUALIFICATION (optional)": "Doctoral degree – Completed"
    #     }
    # )

    app.navigation.click_btn("Next: Work Experience")


@pytest.mark.dependency()
def test_work_experience_vendor_profile(app, login):
    app.vendor_profile.open_tab('Work Experience')

    app.verification.text_present_on_page("STEP 05")
    app.verification.text_present_on_page("Get targeted oportunities by letting us know about your work experience")

    vendor_info = app.vendor_profile.get_information_from_page()
    #assert vendor_info['Customer service/ call centres'] is None
    #assert vendor_info['Translation between your spoken languages'] == 'true'
    #assert vendor_info['Transcribing audio or annotating data'] == 'true'
    #'I have work experience in transcribing audio or annotating data.': 'true', 'I have work experience in proofreading.': 'true', 'I am currently working as a search engine evaluator.': None
    assert vendor_info['I have work experience in transcribing audio or annotating data.'] == 'true'
    assert vendor_info['I have work experience in proofreading.'] == 'true'
    assert vendor_info['I am currently working as a search engine evaluator.'] is None
    app.navigation.click_btn("Next: Phone Number")


@pytest.mark.dependency()
def test_phone_number_vendor_profile(app, login):
    app.vendor_profile.open_tab('Phone Number')
    app.verification.text_present_on_page("STEP 06")
    app.verification.text_present_on_page("Add at least one phone number for personal contact")
    app.verification.text_present_on_page("Mobile Phone Number")

    app.navigation.click_btn("Add Secondary Number")
    vendor_info = app.vendor_profile.get_information_from_page()
    assert vendor_info['MOBILE PHONE NUMBER'] == '+1 (266) 906-4020'
    # assert vendor_info['SECONDARY PHONE NUMBER'] == ''
    app.vendor_profile.phone.fill_out_fields({"Secondary Phone Number": "+1-266-906-4021"})

    # Verify Primary Phone Number is required
    app.vendor_profile.phone.remove_data({"Mobile Phone Number": vendor_info['MOBILE PHONE NUMBER']})
    app.vendor_profile.click_out("Mobile Phone Number")
    app.verification.text_present_on_page("Required field")
    app.vendor_profile.phone.fill_out_fields({"Mobile Phone Number": "266-906-1234"})

    # Verify Secondary Phone Number is required
    app.vendor_profile.phone.remove_data({"Secondary Phone Number": vendor_info['SECONDARY PHONE NUMBER']})
    app.vendor_profile.click_out("Secondary Phone Number")
    app.vendor_profile.phone.fill_out_fields({"Secondary Phone Number": "+1-266-906-9876"})

    app.navigation.click_btn("Next: Preview")
    app.navigation.click_btn("Back")
    vendor_info = app.vendor_profile.get_information_from_page()
    assert vendor_info['MOBILE PHONE NUMBER'] == '+1 (266) 906-1234'
    assert vendor_info['SECONDARY PHONE NUMBER'] == '+1 (266) 906-9876'


@pytest.mark.dependency(depends=["test_basic_information_vendor_profile", "test_languages_vendor_profile",
                                 "test_location_vendor_profile", "test_education_vendor_profile",
                                 "test_work_experience_vendor_profile", "test_phone_number_vendor_profile"])
def test_preview_profile_vendor_profile(app, login):
    app.vendor_profile.open_tab('Preview')
    app.verification.text_present_on_page("STEP 07")
    app.verification.text_present_on_page("Review your information before submitting your profile")

    vendor_info = app.vendor_profile.get_information_from_page()
    print("0-0-", vendor_info)
    assert vendor_info['CONTRACT TYPE'] == 'Registered Business'
    assert vendor_info['BUSINESS NAME'] == 'Vendor ProfileTest'
    assert vendor_info['FIRST NAME'] == _vendor_profile["firstName"]
    assert vendor_info['LAST NAME'] == _vendor_profile["lastName"]
    assert vendor_info['EMAIL'] == _vendor_profile["email"]
    assert vendor_info['YOUR LANGUAGE REGION'] == 'United States of America'
    assert vendor_info['YOUR PRIMARY LANGUAGE'] == 'English'
    assert vendor_info['HIGHEST LEVEL OF EDUCATION'] == 'Doctorate degree or equivalent'
    assert vendor_info['LINGUISTICS QUALIFICATION'] == 'Doctoral degree – Completed'
    assert vendor_info['PRIMARY PHONE'] == '+1 266 906 1234'
    assert vendor_info['SECONDARY PHONE NUMBER'] == '+1 266 906 9876'


# @pytest.mark.skip(reason='Problem on Registration Endpoint ACE-8511')
@pytest.mark.dependency(depends=["test_preview_profile_vendor_profile"])
def test_vendor_submit_profile(app, login):
    app.vendor_profile.open_tab('Preview')

    app.navigation.click_btn("Save and Submit Profile")
    app.navigation.click_btn("Continue")

    app.verification.current_url_contains('core/vendors/projects')

