import pytest

from adap.api_automation.utils.data_util import find_dict_in_array_by_value
from appen_connect.api_automation.services_config.ac_api import AC_API
from appen_connect.api_automation.services_config.ac_sme import SME

# not working, only for local run
# pytestmark = [pytest.mark.regression_ac, pytest.mark.ac_api_sme, pytest.mark.ac_api_sme_functional]

SME_API = SME()

WORKER_SCREENED= 424837
WORKER_CONTRACT_PENDING = 649916  # 664428
WORKER_ACTIVE = 1295273
WORKER_EXPRESS_QUALIFYING = 1294754
WORKER_EXPRESS_ACTIVE = 1294557
WORKER_EXPRESS_TO_BE_CONVERTED = 1294625

WORKER_IS_LOCKED = 596155

WORKER_REJECTED = 1294765
WORKER_ABANDONED = 451957
WORKER_ARCHIVED = 1294604
WORKER_SUSPENDED = 355312
WORKER_TERMINATED = 1294515

WORKER_2_LANGUAGES = 1250027

WORKER_COMPETITOR = 811371


@pytest.fixture(scope='module')
def get_additional_data(ac_api_cookie_no_customer):
    api = AC_API(ac_api_cookie_no_customer)
    _LANGUAGES = api.get_languages().json_response
    _COUNTRIES = api.get_countries().json_response
    return {"LANGUAGES": _LANGUAGES,
            "COUNTRIES": _COUNTRIES}


# user status
@pytest.mark.parametrize('test_name,worker_id, expected_status',
                         [('ACTIVE', WORKER_ACTIVE, 200),
                          ('SCREENED', WORKER_SCREENED, 200),
                          ('CONTRACT_PENDING', WORKER_CONTRACT_PENDING, 200)
                           ])
def test_user_status_non_express(test_name,  worker_id, expected_status):
    payload = {
      "workerId": worker_id,
      "useCase": "allWorkers",
      "maxReturnCount": 10,
      "hireGapThreshold": 0.01,
      "project_types": [
        "TRANSCRIPTION"
      ],
      "languages": [{
        "language_from": "eng",
        "country_from": "USA"
      }]
    }

    res = SME_API.find_projects(payload)
    res.assert_response_status(expected_status)
    assert res.json_response['workerId'] == str(worker_id)
    assert len(res.json_response['projects']) > 0


@pytest.mark.parametrize('test_name,worker_id, expected_status',
                             [('EXPRESS_ACTIVE', WORKER_EXPRESS_ACTIVE, 200),
                              ('EXPRESS_QUALIFYING', WORKER_EXPRESS_QUALIFYING, 200),
                              ('EXPRESS_TO_BE_CONVERTED', WORKER_EXPRESS_TO_BE_CONVERTED, 200)
                              ])
def test_user_status_express_projects(test_name, worker_id, expected_status, ac_api_cookie_no_customer):
    """
    vendor WORKER_EXPRESS_ACTIVE, WORKER_EXPRESS_TO_BE_CONVERTED and WORKER_EXPRESS_QUALIFYING should be qualified only for express projects
    """
    payload = {
        "workerId": worker_id,
        "useCase": "allWorkers",
        "maxReturnCount": 10,
        "hireGapThreshold": 0.01
    }

    res = SME_API.find_projects(payload)
    res.assert_response_status(expected_status)
    assert res.json_response['workerId'] == str(worker_id)
    assert len(res.json_response['projects']) > 0

    api = AC_API(ac_api_cookie_no_customer)
    for project in res.json_response['projects']:
        _id = project['projectId']

        _res = api.get_project_by_id(_id)
        _res.assert_response_status(200)

        assert _res.json_response['projectType'] == 'Express'


def test_account_locked():
    payload = {
        "workerId": WORKER_IS_LOCKED,
        "useCase": "allWorkers",
        "maxReturnCount": 10,
        "hireGapThreshold": 0.1
    }

    res = SME_API.find_projects(payload)
    res.assert_response_status(200)

    assert res.json_response['reasons'] == ["worker is locked",
                "worker status is not one of SCREENED,CONTRACT_PENDING,ACTIVE,EXPRESS_QUALIFYING,EXPRESS_ACTIVE,EXPRESS_TO_BE_CONVERTED"]



@pytest.mark.parametrize('worker_id', [WORKER_REJECTED, WORKER_ABANDONED, WORKER_ARCHIVED, WORKER_SUSPENDED, WORKER_TERMINATED])
def test_rejected_user(worker_id):
    payload = {
        "workerId": worker_id,
        "useCase": "allWorkers",
        "maxReturnCount": 10,
        "hireGapThreshold": 0.1
    }

    res = SME_API.find_projects(payload)
    res.assert_response_status(200)
    assert res.json_response['reasons'][0] == "worker status is not one of SCREENED,CONTRACT_PENDING,ACTIVE," \
                                              "EXPRESS_QUALIFYING,EXPRESS_ACTIVE," \
                                              "EXPRESS_TO_BE_CONVERTED"
    assert res.json_response['status'] == "WORKER_IS_NOT_VALID"
    assert res.json_response['success']


def test_language_match(ac_api_cookie_no_customer, get_additional_data):
    payload = {
        "workerId": WORKER_2_LANGUAGES,
        "useCase": "allWorkers",
        "maxReturnCount": 10,
        "hireGapThreshold": 0.1
    }

    res = SME_API.find_projects(payload)
    res.assert_response_status(200)

    worker_details = SME_API.get_worker_details({"workerId": WORKER_2_LANGUAGES})
    _lan = [x['language_from'] for x in worker_details.json_response['language_skills']]
    _country = [x['country_from'] for x in worker_details.json_response['language_skills']]

    # add language groups
    lan_groups = []
    for current_lan in _lan:
        lan_info = find_dict_in_array_by_value(get_additional_data['LANGUAGES'], 'value', current_lan)
        if lan_info['group']: lan_groups.append(lan_info['group'])

    _lan = _lan + lan_groups

    for _projects in res.json_response['projects']:
        locale = _projects['locale']
        assert locale.split('-')[0] in _lan
        assert locale.split('-')[1] in _country or "*"
        assert locale.split('-')[2] in _country or "*"


@pytest.mark.parametrize('tenant_id,worker_id',
                             [(1, 1124981)
                              # (2, 1194776) bug ACE-6710
                              ])
def test_locale_tenants(tenant_id,  worker_id, ac_api_cookie_no_customer):

    payload = {
        "workerId": worker_id,
        "useCase": "allWorkers",
        "maxReturnCount": 10,
        "hireGapThreshold": 0.1
    }

    res = SME_API.find_projects(payload)
    res.assert_response_status(200)

    matched_projects = res.json_response['projects']

    api_project = AC_API(ac_api_cookie_no_customer)
    for project in matched_projects:
        _id = project['projectId']
        _tenants = [x['tenantId'] for x in api_project.get_locale_tenants(id=_id).json_response]
        assert tenant_id in _tenants


# 	Blocking rules
def test_vendor_working_for_competitor():
    payload = {
        "workerId": WORKER_COMPETITOR,
        "useCase": "allWorkers",
        "maxReturnCount": 10,
        "hireGapThreshold": 0.1
    }

    res = SME_API.find_projects(payload)
    res.assert_response_status(200)

    assert res.json_response['reasons'][0] == "work for \"competitor\"",\
    "worker status is not one of SCREENED,CONTRACT_PENDING,ACTIVE,EXPRESS_QUALIFYING,EXPRESS_ACTIVE," \
    "EXPRESS_TO_BE_CONVERTED "

    assert res.json_response['status'] == "WORKER_IS_NOT_VALID"
    assert res.json_response['success']


@pytest.mark.skip(reason='Bug! ACE-6714')
def test_dnh_states(ac_api_cookie_no_customer):
    payload = {
        "workerId": 1295038,
        "useCase": "allWorkers",
        "maxReturnCount": 10,
        "hireGapThreshold": 0.01
    }

    res = SME_API.find_projects(payload)
    res.assert_response_status(200)
    assert len(res.json_response['projects']) > 0

    api = AC_API(ac_api_cookie_no_customer)
    for project in res.json_response['projects']:
        _id = project['projectId']

        _res = api.get_project_by_id(_id)
        _res.assert_response_status(200)

        assert _res.json_response['projectType'] == 'Regular'


@pytest.mark.skip(reason='Bug! ACE-6714')
def test_dnh_states_express(ac_api_cookie_no_customer):
    # dnh and express - 1294807
    payload = {
        "workerId": 1294807,
        "useCase": "allWorkers",
        "maxReturnCount": 10,
        "hireGapThreshold": 0.01
    }

    res = SME_API.find_projects(payload)
    res.assert_response_status(200)
    assert len(res.json_response['projects']) == 0


def test_customer_blocking_rule():
    payload = {
        "workerId": 1278637,
        "useCase": "allWorkers",
        "maxReturnCount": 10,
        "hireGapThreshold": 0.01
    }

    res = SME_API.find_projects(payload)
    res.assert_response_status(200)
    matched_projects = [x['projectId'] for x in res.json_response['projects']]
    blocked_ids = [105, 164, 518, 252]  # filterruleidx.blocked_project_ids for that given user in ES

    assert len(set(matched_projects).intersection(set(blocked_ids))) == 0




# def test_temp(ac_api_cookie_no_customer):
#     pass
# error msg if payload is not valid
# "hireGapThreshold": 1.1  > 1 success?
#project blocking rules



# account locked
#  locale_lang, locale_dialect and restricted_to_country
# Hiring Target - gap



# filter - project  type, language