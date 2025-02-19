import datetime
from appen_connect.api_automation.services_config.ac_api import AC_API
from appen_connect.ui_automation.service_config.project.project_helper import generate_project_name

config = {}

DEFAULT_INVOICE_PAYLOAD = {
    "disableUserReportTime":'false',
    "autoApproveInvoice":'false',
    "autoGenerateInvoice":'false',
    "invoiceLineItemApproval":'false',
    "requiresPMApproval":'false',
    "autoRejectInvoice":'false',
    "configuredInvoice":'true'
}

# DEFAULT_PAYLOAD = {
#     "acanProject": 'true',
#     "alias": _project[1],
#     "allowedIps": [
#         "string"
#     ],
#     "blockingRules": [
#         {
#             "blockedProjectId": 0,
#             "permanent": 'true'
#         }
#     ],
#     "businessUnit": "CR",
#     "createdBy": {
#         "email": "string",
#         "firstName": "string",
#         "fullName": "string",
#         "id": 0,
#         "lastName": "string",
#         "phone": "string",
#         "roles": [
#             "ROLE_USER"
#         ]
#     },
#     "customerId": 0,
#     "defaultPageId": 0,
#     "demographicsTargetType": "PERCENT",
#     "description": "string",
#     "externalSystemId": 0,
#     "financeNotes": "string",
#     "linkedProjectsIds": [
#         0
#     ],
#     "name": _project[0],
#     "partnerData": 'true',
#     "productivityData": 'true',
#     "projectType": "string",
#     "qualificationProcessTemplateId": 0,
#     "rateType": "HOURLY",
#     "recruitingTeamNotes": "string",
#     "registrationProcessTemplateId": 0,
#     "skillsReview": 'true',
#     "status": "DRAFT",
#     "supportTeam": [
#         {
#             "role": "QUALITY",
#             "userId": 0
#         }
#     ],
#     "swfhProjectExternalUrl": "string",
#     "taskVolume": "VERY_LOW",
#     "workType": "LINGUISTICS",
#     "workdayTaskId": "CR99912"
# }

def get_simple_payload():
    _project = generate_project_name()

    simple_payload = {
        "alias": _project[1],
        "businessUnit": "CR",
        "workdayTaskId": "CR99912",
        "customerId": 53, # Appen Internal
        # "defaultPageId": 0,
        "description": "Test Project" + _project[1],
        "name": _project[0],
        "projectType": "Regular",
        "qualificationProcessTemplateId": 3,
        "rateType": "HOURLY",
        "registrationProcessTemplateId": 4,
        "status": "DRAFT",
        "externalSystemId": 15,
        "profileTargetId": "",
        "supportTeam": [
            {
                "userId": 1294799,
                "role": "RECRUITING"
            }],
        "taskVolume": "VERY_LOW",
        "workType": "LINGUISTICS"
    }

    return simple_payload


def api_create_simple_project(new_config=None, cookies=None, env=None) -> object:
    api = AC_API(cookies=cookies, env=env)

    # overwrite params from config
    _payload = get_simple_payload()
    print("new conf", new_config)
    if new_config:
        print("change config")
        for key, value in new_config.items():
            print("-=-=", key, "- ",value)
            if key in _payload.keys():
                print("overwrite")
                _payload[key] = value


    print(_payload)
    res = api.create_project(payload=_payload)
    print(res.json_response)
    res.assert_response_status(201)

    project_id = res.json_response['id']

    locale_payload = {
        "country": "RUS",
        "projectId": "{project_id}".format(project_id=project_id),
        "tenantId": 1
    }

    # overwrite params from config
    CREATE_LOCALE = True
    _locale_payload = locale_payload
    if new_config and new_config.get('locale'):
        for key, value in new_config['locale'].items():
            if key == 'create' and value == False: CREATE_LOCALE = False
            if _locale_payload.get(key):
                _locale_payload[key] = value

    if CREATE_LOCALE:
        locale = api.create_locale_tenant(payload=locale_payload)
        locale.assert_response_status(201)
    else:
        return project_id

    tomorrow = (datetime.datetime.today() + datetime.timedelta(days=1)).isoformat()

    CREATE_HIRING_TARGET = True
    hiring_target_payload = {
        "deadline": tomorrow,
        "language": "rus",
        "languageCountry": "RUS",
        "languageCountryTo": "",
        "languageTo": "",
        "ownerId": 0,
        "priority": 0,
        "projectId": project_id,
        "restrictToCountry": "RUS",
        "target": 1
    }

    # overwrite hiring target from config
    _hiring_target_payload = hiring_target_payload
    if new_config and new_config.get('hiring_target'):
        for key, value in new_config['hiring_target'].items():
            if key == 'create' and value == False: CREATE_HIRING_TARGET = False
            if _hiring_target_payload.get(key):
                _hiring_target_payload[key] = value

    if CREATE_HIRING_TARGET:
        hir_target = api.add_hiring_target(_hiring_target_payload)
        hir_target.assert_response_status(201)
    else:
        return project_id

    # ------ PAY RATES -----------
    CREATE_PAY_RATES = True
    pay_rates_payload = {
                         "projectId": project_id,
                         "writtenFluency": "NATIVE_OR_BILINGUAL",
                         "spokenFluency": "NATIVE_OR_BILINGUAL",
                         "rateValue": 5,
                         # "disabled": false,
                         "language": "rus",
                         "languageCountry": "RUS",
                         "languageTo": "",
                         "languageCountryTo": "",
                         "restrictToCountry": "RUS",
                         "groupId": 1,
                         "taskType": "DEFAULT",
                         "defaultRate": 'true',
                         "countryPayRateId": 9
    }

    _pay_rates_payload = pay_rates_payload
    if new_config and new_config.get('pay_rates'):
        for key, value in new_config['pay_rates'].items():
            if key == 'create' and value == False: CREATE_PAY_RATES = False
            if _pay_rates_payload.get(key):
                _pay_rates_payload[key] = value

    if CREATE_PAY_RATES:
        pay_rates = api.create_pay_rate(pay_rates_payload)
        pay_rates.assert_response_status(201)

    # update invoice config
    if new_config.get("invoice"):
        if new_config.get("invoice") == 'default':
            invoice_payload = DEFAULT_INVOICE_PAYLOAD
        else:
            invoice_payload = new_config['invoice']

        invoice = api.update_invoice_configuration(project_id, invoice_payload)
        invoice.assert_response_status(200)

    #  update user group - add all user group
    if new_config.get("all_users"):
        res = api.get_experiments_for_project(project_id)
        res.assert_response_status(200)

        experiment_info = res.json_response[0]["id"]
        payload = [{"experimentId": experiment_info, "groupId": 1}]

        res = api.update_experiment_group(experiment_info, payload)
        res.assert_response_status(200)


    # update project status, by default DRAFT
    if new_config.get("update_status"):
        if new_config.get("update_status") == "ENABLED":
            status_payload = {
                "status": "READY"
            }
            status = api.update_project_status(project_id, status_payload)
            status.assert_response_status(200)

        status_payload = {
            "status": new_config['update_status']
        }
        status = api.update_project_status(project_id, status_payload)
        status.assert_response_status(200)

    return {"id":project_id,
            "name": _payload['name'],
            "alias": _payload['alias']}


 # example for project payload config. if config={} - function uses default config
# examples:
#  default project:
#    config = {}
#
#  default project without locale:
#  config = {
#         "locale": {
#             "create": False
#         }
#     }
#
# express linguistic project with locale USA and hiring Target eng-USA:
# config = {
#     "projectType": 'Express',
#     "workType": "LINGUISTICS",
#     "locale": {
#         "country": "USA"
#     },
#     "hiring_target": {
#         "language": "eng",
#         "languageCountry": "USA",
#         "restrictToCountry": "USA"
#     },
#     "pay_rates": {
#         "create": False
#     }
# }
#
#  update project status  DRAFT/READY/ENABLED/DISABLED
#    config = {
#        "update_status":"READY"
#    }
#
# example: create project with default invoice
# config = {
#     "invoice":"default"
# }
#
# for custom invoice configuration  - provide custom payload
# config={
#     "invoice":{
#          "disableUserReportTime":'true',
#          "autoApproveInvoice":'false',
#     }
# }

# NOTE: remember locale, hiring targets, and pay rates depend on each other if one of them will be change - need to change rest one

# def test_new_project_temp(ac_api_cookie):
    # config = {}
    # api_create_simple_project(config, ac_api_cookie)