# """
# This test covers Appen Connect mobile api e2e testing from vendor (worker) perspective.
# https://appen.atlassian.net/wiki/spaces/ENGR/pages/5305958417/E2e+Positive+Test
# The flow is like:
# 1. Create a new vendor, find project 6650 which is ready to apply, call api to apply it, make it ready to complete intelligence attribute
# 2. Call api to finish intelligence attribute form
# 3. Call document signature api
# https://appen.atlassian.net/browse/QED-2490  apply the project
# https://appen.atlassian.net/browse/QED-2290  call user service before and after apply.
# https://appen.atlassian.net/browse/QED-2474 smartphone collection
# https://appen.atlassian.net/browse/QED-2451 third party signature
# https://appen.atlassian.net/browse/QED-2496 document signature api
# """
# from jenkins_support.deprecated.mobile_app_apis.mobile_api_old import *
# from adap.api_automation.utils.data_util import *
# import time
#
# INTERNAL_USER_NAME = get_user_email('test_ui_account')
# PASSWORD = get_user_password('test_ui_account')
# VERIFICATION_CODE = "6DECDC"
# PROJECT_ID_TO_APPLY = 6650
#
# pytestmark = [
#               # pytest.mark.regression_ac_core,  tests are not working
#               pytest.mark.regression_ac,
#               pytest.mark.ac_api_mobile,
#               pytest.mark.ac_api_mobile_e2e,
#               pytest.mark.ac_api]
#
#
# @pytest.fixture(scope="module")
# def create_new_vendor_and_get_cookie(app):
#     global new_vendor_user_name
#     new_vendor_user_name = "sandbox+" + str(random.randint(10000000, 99999999)) + "@figure-eight.com"
#     app.vendor_profile.registration_flow.register_user(user_name=new_vendor_user_name, user_password=PASSWORD,
#                                                        user_first_name="firstname", user_last_name="lastname",
#                                                        residence_value='United States of America', state='Alabama')
#     app.vendor_profile.registration_flow.fill_out_fields({"CERTIFY DATA PRIVACY": 1,
#                                                           "CERTIFY SSN": 1}, action="Create Account")
#     app.vendor_profile.registration_flow.fill_out_fields({"VERIFICATION CODE": VERIFICATION_CODE},
#                                                          action="Verify Email")
#
#     app.verification.text_present_on_page("Account Created")
#     app.navigation.click_btn("Go to Login page")
#     # get vendor_id for future use
#     app.ac_user.login_as(user_name=INTERNAL_USER_NAME, password=PASSWORD)
#     app.navigation.maximize_window()
#     app.navigation.switch_to_frame("page-wrapper")
#     app.navigation.click_btn("Skip")
#     app.driver.switch_to.default_content()
#     app.navigation.click_link('Internal Home')
#     app.navigation.click_link("Vendors")
#     app.vendor_pages.open_vendor_profile_by(new_vendor_user_name, search_type='name', status='Any Status')
#     global vendor_id
#     vendor_id = app.vendor_pages.get_vendor_id()
#     app.navigation.click_link("Logout")
#
#     app.ac_user.login_as(user_name=new_vendor_user_name, password=PASSWORD)
#     app.verification.current_url_contains('/qrp/core/vendors/primary_language')
#     app.navigation.switch_to_frame("page-wrapper")
#     app.verification.text_present_on_page("Language")
#     app.vendor_profile.registration_flow.fill_out_fields({"YOUR PRIMARY LANGUAGE": "English",
#                                                           "YOUR LANGUAGE REGION": "United States of America"})
#     app.navigation.click_btn("Continue")
#     app.navigation.switch_to_frame("page-wrapper")
#     app.verification.text_present_on_page("Welcome")
#     app.verification.text_present_on_page("Get started now!")
#     app.verification.text_present_on_page("Complete profile")
#     app.verification.text_present_on_page("Browse jobs")
#     app.vendor_profile.registration_flow.get_start_from_welcome_page("Complete profile")
#     flat_cookie_dict = {seleniumCookie['name']: seleniumCookie['value'] for seleniumCookie in app.driver.get_cookies()}
#     return flat_cookie_dict
#
#
# """
# https://appen.atlassian.net/browse/QED-2490  [AC] [API] Project Registration
# 1.Start project registration, call get all projects api to get all projects for vendor
# 2.Choose one project ready to apply from the list
# 3.Call post api to apply the project
# 4.Call get all project api again to make sure the applied project in "APPLIED_OPTIONS" status
# 5.Call post api again, verify 409 response status
# """
#
#
# @pytest.mark.dependency()
# def test_get_all_projects_and_user_service_before_apply(create_new_vendor_and_get_cookie):
#     api = MOBILE_APIS(create_new_vendor_and_get_cookie)
#     res = api.get_all_projects(vendor_id)
#     res.assert_response_status(200)
#     assert len(res.json_response.get("projects")) > 0
#     random_index = random.randrange(0, len(res.json_response.get("projects")))
#     projects = res.json_response.get("projects")[random_index]
#     assert "projectId" in projects
#     assert "projectName" in projects
#     assert "projectAlias" in projects
#     assert "projectDescription" in projects
#     assert "workType" in projects
#     assert "rate" in projects
#     assert "taskWorkload" in projects
#     assert "category" in projects
#     assert "rankScore" in projects
#     assert "suggestedOrder" in projects
#     assert "suggested" in projects
#     assert "applied" in projects
#     assert "myProject" in projects
#     assert "actions" in projects
#     # find one project with "APPLY" status
#     for i in range(0, len(res.json_response.get("projects"))):
#         projectid = res.json_response.get("projects")[i].get("projectId")
#         if projectid == PROJECT_ID_TO_APPLY:
#             actions = res.json_response.get("projects")[i].get("actions")[0]
#             assert actions == "APPLY"
#             break
#
#     res = api.get_user_service(vendor_id, PROJECT_ID_TO_APPLY)
#     res.assert_response_status(200)
#     assert res.json_response == {}
#
#
# @pytest.mark.dependency(depends=["test_get_all_projects_and_user_service_before_apply"])
# def test_apply_project_mobile(create_new_vendor_and_get_cookie):
#     api = MOBILE_APIS(create_new_vendor_and_get_cookie)
#     # Apply the project
#     payload = \
#         {
#             "userId": vendor_id,
#             "projectId": PROJECT_ID_TO_APPLY
#         }
#     apply_res = api.post_apply_projects(payload)
#     apply_res.assert_response_status(200)
#     # After apply, call get all project api again, check the options status for the project just applied,
#     # make sure it is APPLIED_OPTIONS
#     time.sleep(8)
#     res = api.get_all_projects(vendor_id)
#     res.assert_response_status(200)
#     for i in range(0, len(res.json_response.get("projects"))):
#         projectid = res.json_response.get("projects")[i].get("projectId")
#         if projectid == PROJECT_ID_TO_APPLY:
#             assert res.json_response.get("projects")[i].get("actions")[0] == "APPLIED_OPTIONS"
#             break
#     # Call apply project api again, verify 409 response status
#     apply_res = api.post_apply_projects(payload)
#     apply_res.assert_response_status(409)
#     assert "User " + str(vendor_id) + " is already REGISTERED on project " + str(PROJECT_ID_TO_APPLY) + "." == apply_res.json_response.get("error")
#
#
# # Below four are negative cases for apply project api
# def test_apply_project_invalid_project_id(create_new_vendor_and_get_cookie):
#     api = MOBILE_APIS(create_new_vendor_and_get_cookie)
#     payload = \
#         {
#             "userId": vendor_id,
#             "projectId": 9999
#         }
#     res = api.post_apply_projects(payload)
#     res.assert_response_status(500)
#     assert res.json_response.get("code") == "E00"
#     assert res.json_response.get("error") == "Unknown error"
#
#
# def test_apply_project_invalid_user_id(create_new_vendor_and_get_cookie):
#     api = MOBILE_APIS(create_new_vendor_and_get_cookie)
#     res = api.get_all_projects(vendor_id)
#     random_index = random.randrange(0, len(res.json_response.get("projects")))
#     projectid = res.json_response.get("projects")[random_index].get("projectId")
#     payload = \
#         {
#             "userId": 9999,
#             "projectId": projectid
#         }
#     res = api.post_apply_projects(payload)
#     res.assert_response_status(403)
#     assert res.json_response == {}
#
#
# @pytest.mark.dependency(depends=["test_apply_project_mobile"])
# def test_apply_project_no_cookie():
#     api = MOBILE_APIS()
#     payload = \
#         {
#             "userId": vendor_id,
#             "projectId": PROJECT_ID_TO_APPLY
#         }
#     res = api.post_apply_projects(payload)
#     res.assert_response_status(500)
#     assert res.json_response == {}
#
#
# """
# https://appen.atlassian.net/browse/QED-2290   [AC] [API] user-service/processes
# 1.Call get user service api for project applied above in scenario QED-2490, check status
# 2.Several negative cases for get user service api
# """
#
#
# @pytest.mark.dependency(depends=["test_apply_project_mobile"])
# def test_user_service_after_apply(create_new_vendor_and_get_cookie):
#     api = MOBILE_APIS(create_new_vendor_and_get_cookie)
#     res = api.get_user_service(vendor_id, PROJECT_ID_TO_APPLY)
#     res.assert_response_status(200)
#     assert res.json_response.get("taskName") == "Complete intelligent attributes"
#     assert "formButtons" in res.json_response
#     assert "formElements" in res.json_response
#     assert "text" in res.json_response
#
#
# # Login with different user, return 403
# @pytest.mark.dependency(depends=["test_apply_project_mobile"])
# def test_user_service_process_different_user(ac_api_cookie):
#     api = MOBILE_APIS(ac_api_cookie)
#     res = api.get_user_service(vendor_id, PROJECT_ID_TO_APPLY)
#     res.assert_response_status(403)
#     assert res.json_response == {}
#
#
# # no cookie, expecting 200, but return 500??????????
# @pytest.mark.dependency(depends=["test_apply_project_mobile"])
# def test_user_service_no_cookie():
#     api = MOBILE_APIS()
#     res = api.get_user_service(vendor_id, PROJECT_ID_TO_APPLY)
#     res.assert_response_status(500)
#     assert res.json_response == {}
#
#
# def test_user_service_invalid_project_id(create_new_vendor_and_get_cookie):
#     api = MOBILE_APIS(create_new_vendor_and_get_cookie)
#     res = api.get_user_service(vendor_id, "abcd")
#     res.assert_response_status(500)
#     assert res.json_response.get("code") == "E00"
#     assert res.json_response.get("error") == "Unknown error"
#
#
# """
# https://appen.atlassian.net/browse/QED-2289   [AC] [API] Intelligent Attributes
# 1.Call post intelligent attribute api with invalid user id and invalid payload for some negative cases.
# 2.Call get user service api, get response, compose intelligent attribute api payload based on user service api response, then call intelligent attribute api for positive case
# 3.After calling intelligent attribute api successfully, call get user service api again, make sure it is in "Data Collection PII Consent Form" status
# """
#
#
# # Login with different user, return 403
# def test_post_intelligent_attribute_different_user(ac_api_cookie):
#     api = MOBILE_APIS(ac_api_cookie)
#     payload = {'lpid': '9b572ec776e814533beef2b595a2f0ce', 'userId': '1295920', 'projectId': '263', 'attributes': {'884': {'intelligentAttributeId': '884', 'stringValue': '1985-03-27'}, '728': {'intelligentAttributeId': '728', 'stringValue': 'abk'}}}
#     res = api.post_intelligent_attribute(vendor_id, payload, ac_api_cookie)
#     res.assert_response_status(403)
#     assert res.json_response.get("code") == "E05"
#     assert res.json_response.get("error") == "Error calling service endpoint"
#
#
# def test_post_intelligent_attribute_no_cookie():
#     api = MOBILE_APIS()
#     payload = {'lpid': '9b572ec776e814533beef2b595a2f0ce', 'userId': '1295920', 'projectId': '263', 'attributes': {'884': {'intelligentAttributeId': '884', 'stringValue': '1985-03-27'}, '728': {'intelligentAttributeId': '728', 'stringValue': 'abk'}}}
#     res = api.post_intelligent_attribute(vendor_id, payload)
#     res.assert_response_status(500)
#     assert res.json_response == {}
#
#
# @pytest.mark.dependency(depends=["test_user_service_after_apply"])
# def test_post_intelligent_attribute_empty_attributes_payload(create_new_vendor_and_get_cookie):
#     api = MOBILE_APIS(create_new_vendor_and_get_cookie)
#     res = api.get_user_service(vendor_id, PROJECT_ID_TO_APPLY)
#     res.assert_response_status(200)
#     attribute = res.json_response.get("formElements")
#     attribute_payload = {"lpid": "", "userId": "", "projectId": "", "attributes": {}}
#     attribute_payload.update({'lpid': attribute[0].get("value")})
#     attribute_payload.update({'userId': vendor_id})
#     attribute_payload.update({'projectId': attribute[1].get("value")})
#     res = api.post_intelligent_attribute(vendor_id, attribute_payload, create_new_vendor_and_get_cookie)
#     res.assert_response_status(422)
#     assert res.json_response.get("code") == "E09"
#     assert res.json_response.get("error") == "Validation error"
#     assert "field" in res.json_response.get("fieldErrors")[0]
#     assert "message" in res.json_response.get("fieldErrors")[0]
#     assert "code" in res.json_response.get("fieldErrors")[0]
#
#
# @pytest.mark.dependency(depends=["test_user_service_after_apply"])
# def test_post_intelligent_attribute_invalid_payload_value(create_new_vendor_and_get_cookie):
#     api = MOBILE_APIS(create_new_vendor_and_get_cookie)
#     res = api.get_user_service(vendor_id, PROJECT_ID_TO_APPLY)
#     res.assert_response_status(200)
#     attribute = res.json_response.get("formElements")
#     attribute_payload = {"lpid": "", "userId": "", "projectId": "", "attributes": ""}
#     attribute_payload.update({'lpid': attribute[0].get("value")})
#     attribute_payload.update({'userId': vendor_id})
#     attribute_payload.update({'projectId': attribute[1].get("value")})
#
#     # compose attributes for the payload
#     attribute_len = len(res.json_response.get("formElements"))
#     attributes_json = {}
#     for i in range(2, attribute_len):
#         name = attribute[i].get("name")
#         name = name[11:len(name) - 1]
#         attributes_json.update({name: {
#            "intelligentAttributeId": name,
#            "stringValue": str(random.randint(1, 10))
#         }})
#
#     attribute_payload.update({'attributes': attributes_json})
#     res = api.post_intelligent_attribute(vendor_id, attribute_payload, create_new_vendor_and_get_cookie)
#     res.assert_response_status(422)
#     assert res.json_response.get("code") == "E09"
#     assert res.json_response.get("error") == "Validation error"
#     assert "field" in res.json_response.get("fieldErrors")[0]
#     assert "message" in res.json_response.get("fieldErrors")[0]
#     assert res.json_response.get("fieldErrors")[0].get("code") == "UserIntelligentAttributeValid"
#
#
# # Step 6 from https://appen.atlassian.net/wiki/spaces/ENGR/pages/5305958417/E2e+Positive+Test
# @pytest.mark.dependency(depends=["test_user_service_after_apply"])
# def test_post_intelligent_attribute_positive_case(create_new_vendor_and_get_cookie):
#     api = MOBILE_APIS(create_new_vendor_and_get_cookie)
#     res = api.get_user_service(vendor_id, PROJECT_ID_TO_APPLY)
#     res.assert_response_status(200)
#     attribute = res.json_response.get("formElements")
#     attribute_payload = {"lpid": "", "userId": "", "projectId": "", "attributes": ""}
#     attribute_payload.update({'lpid': attribute[0].get("value")})
#     attribute_payload.update({'userId': vendor_id})
#     attribute_payload.update({'projectId': attribute[1].get("value")})
#
#     # compose attributes for the payload
#     attribute_len = len(res.json_response.get("formElements"))
#     attributes_json = {}
#     for i in range(2, attribute_len):
#         name = attribute[i].get("name")
#         name = name[11:len(name) - 1]
#         options = attribute[i].get("options")
#         # None means you need to compose StringValue yourself
#         if attribute[i].get("displayName") == "Birthday" or attribute[i].get("displayName") == "input your age" or attribute[i].get("displayName") == "AGE":
#             string_value = "1985-03-27"
#         elif attribute[i].get("displayName") == "input your email":
#             string_value = "sandbox+1610097@figure-eight.com"
#         elif attribute[i].get("displayName") == "input a link":
#             string_value = "https://appen.com/"
#         elif str(options) == "None":
#             string_value = str(random.randint(30, 40))
#         else:
#             string_value = list(options[0].keys())[0]
#
#         attributes_json.update({name: {
#            "intelligentAttributeId": name,
#            "stringValue": string_value
#         }})
#
#     attribute_payload.update({'attributes': attributes_json})
#
#     # call post intelligent attribute api
#     res = api.post_intelligent_attribute(vendor_id, attribute_payload, create_new_vendor_and_get_cookie)
#     res.assert_response_status(200)
#     assert str(res.json_response.get("message")) == "None"
#
#
# # Step 7 from https://appen.atlassian.net/wiki/spaces/ENGR/pages/5305958417/E2e+Positive+Test
# @pytest.mark.dependency(depends=["test_post_intelligent_attribute_positive_case"])
# def test_user_service_after_finish_intelligent_attribute(create_new_vendor_and_get_cookie):
#     api = MOBILE_APIS(create_new_vendor_and_get_cookie)
#     res = api.get_user_service(vendor_id, PROJECT_ID_TO_APPLY)
#     res.assert_response_status(200)
#     assert res.json_response.get("taskName") == "Data Collection PII Consent Form"
#     assert "formButtons" in res.json_response
#     assert "formElements" in res.json_response
#     assert "text" in res.json_response
#
#
# """
# https://appen.atlassian.net/browse/QED-2496   [AC][API] Sign Document
# 1. Call document signature api
# 2. After signature, call get user service api, make sure status in "Sign document"
# 3. Call document signature api again
# """
#
#
# # Step 8 from https://appen.atlassian.net/wiki/spaces/ENGR/pages/5305958417/E2e+Positive+Test
# @pytest.mark.dependency(depends=["test_user_service_after_finish_intelligent_attribute"])
# def test_document_signature_positive(create_new_vendor_and_get_cookie):
#     api = MOBILE_APIS(create_new_vendor_and_get_cookie)
#     res = api.get_user_service(vendor_id, PROJECT_ID_TO_APPLY)
#     res.assert_response_status(200)
#     attribute = res.json_response.get("formElements")
#     attribute_payload = {"lpid": "", "username": "", "password": "", "documentId": "",
#                          "dataCollectionConsentForm": "", "parametersId": ""}
#     attribute_payload.update({'username': new_vendor_user_name})
#     attribute_payload.update({'password': PASSWORD})
#     for i in range(0, len(attribute)):
#         if attribute[i].get("name") == "lpid":
#             attribute_payload.update({'lpid': attribute[i].get("value")})
#         if attribute[i].get("name") == "documentId":
#             attribute_payload.update({'documentId': attribute[i].get("value")})
#         if attribute[i].get("name") == "dataCollectionConsentForm":
#             attribute_payload.update({'dataCollectionConsentForm': attribute[i].get("value")})
#         if attribute[i].get("name") == "parametersId":
#             attribute_payload.update({'parametersId': attribute[i].get("value")})
#     post_res = api.post_document_signature(vendor_id, attribute_payload, create_new_vendor_and_get_cookie)
#     post_res.assert_response_status(200)
#     assert str(post_res.json_response.get("message")) == "None"
#
#
# # Step 9 from https://appen.atlassian.net/wiki/spaces/ENGR/pages/5305958417/E2e+Positive+Test
# @pytest.mark.dependency(depends=["test_document_signature_positive"])
# def test_user_service_after_document_signature(create_new_vendor_and_get_cookie):
#     api = MOBILE_APIS(create_new_vendor_and_get_cookie)
#     res = api.get_user_service(vendor_id, PROJECT_ID_TO_APPLY)
#     res.assert_response_status(200)
#     assert res.json_response.get("taskName") == "Sign document"
#     assert "formButtons" in res.json_response
#     assert "formElements" in res.json_response
#     assert "text" in res.json_response
#
#
# # Step 10 from https://appen.atlassian.net/wiki/spaces/ENGR/pages/5305958417/E2e+Positive+Test
# @pytest.mark.dependency()
# @pytest.mark.dependency(depends=["test_user_service_after_finish_intelligent_attribute"])
# def test_document_signature_again(create_new_vendor_and_get_cookie):
#     api = MOBILE_APIS(create_new_vendor_and_get_cookie)
#     res = api.get_user_service(vendor_id, PROJECT_ID_TO_APPLY)
#     res.assert_response_status(200)
#     attribute = res.json_response.get("formElements")
#     attribute_payload = {"lpid": "", "username": "", "password": "", "documentId": "",
#                           "parametersId": ""}
#     attribute_payload.update({'username': new_vendor_user_name})
#     attribute_payload.update({'password': PASSWORD})
#     for i in range(0, len(attribute)):
#         if attribute[i].get("name") == "lpid":
#             attribute_payload.update({'lpid': attribute[i].get("value")})
#         if attribute[i].get("name") == "documentId":
#             attribute_payload.update({'documentId': attribute[i].get("value")})
#         if attribute[i].get("name") == "parametersId":
#             attribute_payload.update({'parametersId': attribute[i].get("value")})
#     res = api.post_document_signature(vendor_id, attribute_payload, create_new_vendor_and_get_cookie)
#     res.assert_response_status(200)
#     assert str(res.json_response.get("message")) == "None"
#
#
# # Step 11 from https://appen.atlassian.net/wiki/spaces/ENGR/pages/5305958417/E2e+Positive+Test
# @pytest.mark.dependency(depends=["test_document_signature_again"])
# def test_user_service_after_second_document_signature(create_new_vendor_and_get_cookie):
#     api = MOBILE_APIS(create_new_vendor_and_get_cookie)
#     res = api.get_user_service(vendor_id, PROJECT_ID_TO_APPLY)
#     res.assert_response_status(200)
#     assert res.json_response.get("taskName") == "Complete smartphone profile"
#     assert "formButtons" in res.json_response
#     assert "formElements" in res.json_response
#     assert "text" in res.json_response
#
#
# # https://appen.atlassian.net/browse/QED-2451
# def test_third_party_signature_no_cookie():
#     api = MOBILE_APIS()
#     res = api.get_third_party_signature(4989, 1295318)
#     res.assert_response_status(500)
#
#
# def test_third_party_signature_no_parameter(create_new_vendor_and_get_cookie):
#     api = MOBILE_APIS(create_new_vendor_and_get_cookie)
#     res = api.get_third_party_signature()
#     res.assert_response_status(400)
#     assert res.json_response.get("code") == "UNSPECIFIED_ERROR"
#     assert res.json_response.get("message") == "Something went wrong, please try again soon"
#
#
# def test_post_third_party_signature_forbidden(create_new_vendor_and_get_cookie):
#     api = MOBILE_APIS(create_new_vendor_and_get_cookie)
#     payload = {
#       "age": 2,
#       "completedAt": "2021-04-27T17:31:06.795Z",
#       "email": "fmichalach@appen.com",
#       "firstName": "Fatima",
#       "gender": "Other",
#       "id": 264,
#       "lastName": "tesgrijegheiruh",
#       "lastSentAt": "1619634242201",
#       "projectId": 4989,
#       "sendCount": 0,
#       "status": "PENDING",
#       "userId": 1295318
#     }
#     res = api.post_third_party_signature(payload)
#     res.assert_response_status(403)
#
# # Need information from Fatima on how to prepare data and simulate this call
# # def test_post_third_party_signature(create_new_vendor_and_get_cookie):
# #     api = MOBILE_APIS(create_new_vendor_and_get_cookie)
# #     res = api.get_all_projects(vendor_id)
# #     res.assert_response_status(200)
# #     projectid = res.json_response.get("projects")[0].get("projectId")
# #     payload = {
# #       "age": 2,
# #       "completedAt": "2021-04-27T17:31:06.795Z",
# #       "email": "fmichalach@appen.com",
# #       "firstName": "Fatima",
# #       "gender": "Other",
# #       "id": 264,
# #       "lastName": "tesgrijegheiruh",
# #       "lastSentAt": "1619634242201",
# #       "projectId": projectid,
# #       "sendCount": 0,
# #       "status": "PENDING",
# #       "userId": vendor_id
# #     }
# #     res = api.post_third_party_signature(payload)
# #     res.assert_response_status(400)
# #     assert res.json_response.get("code") == "DataCollectionConsentFormNotFound"
# #     assert res.json_response.get("message") == "Cannot retrieve the consent form for the current project."
