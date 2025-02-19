from appen_connect.api_automation.services_config.ac_api import AC_API, create_new_random_project
from adap.api_automation.utils.data_util import *

pytestmark = [pytest.mark.regression_ac_project_config, pytest.mark.regression_ac, pytest.mark.ac_api_v2, pytest.mark.ac_api_v2_invoice, pytest.mark.ac_api]


@pytest.fixture(scope="module")
def new_project_invoice(ac_api_cookie):
    new_project_api = AC_API(ac_api_cookie)
    new_project = create_new_random_project(new_project_api)
    project_id = new_project['output']['id']
    return project_id
    # return 4793


def test_get_invoice_no_cookies(new_project_invoice):
    ac_api = AC_API()
    res = ac_api.get_invoice_configuration(id=new_project_invoice)
    res.assert_response_status(401)
    assert res.json_response == {'error': 'Unauthorized'}


@pytest.mark.parametrize('id, expected_status, error_msg',
                         [('', 400, {"code":"UNSPECIFIED_ERROR","message":"Something went wrong, please try again soon"}),
                          ('one', 400, {"code":"UNSPECIFIED_ERROR","message":"Something went wrong, please try again soon"}),
                          ('!!!!', 400, {"code":"UNSPECIFIED_ERROR","message":"Something went wrong, please try again soon"}),
                          ('9999999', 404, {}),
                          (' ', 400, {'code': None, 'message': 'Project id is null'})])
def test_get_invoice_invalid_project_id(ac_api_cookie, id, expected_status, error_msg):
    ac_api = AC_API(ac_api_cookie)
    res = ac_api.get_invoice_configuration(id=id)
    res.assert_response_status(expected_status)
    assert res.json_response == error_msg


def test_get_no_invoice(ac_api_cookie, new_project_invoice):
    ac_api = AC_API(ac_api_cookie)
    res = ac_api.get_invoice_configuration(id=new_project_invoice)
    res.assert_response_status(200)
    assert res.json_response == {
                       "projectId":new_project_invoice,
                       "configuredInvoice":False,
                       "autoGenerateInvoice":False,
                       "autoApproveInvoice":False,
                       "autoRejectInvoice":False,
                       "invoiceLineItemApproval":False,
                       "requiresPMApproval":False,
                       "disableUserReportTime":False,
                       "projectInvoiceVarianceThreshold":None,
                       "autoGenerateInvoiceBasedon":None,
                       "autoApproveInvoiceBasedon":None
                    }


def test_put_invoice_no_cookies(new_project_invoice):
    ac_api = AC_API()
    payload = {}
    res = ac_api.update_invoice_configuration(id=new_project_invoice, payload=payload)
    res.assert_response_status(401)
    assert res.json_response == {'error': 'Unauthorized'}


@pytest.mark.parametrize('id, expected_status, error_msg',
                         [('', 405, {}),
                          ('one', 400, {"code":"UNSPECIFIED_ERROR","message":"Something went wrong, please try again soon"}),
                          ('!!!!', 400, {"code":"UNSPECIFIED_ERROR","message":"Something went wrong, please try again soon"}),
                          ('9999999', 404, {}),
                          (' ', 400, {'code': None, 'message': 'Project id is null'})])
def test_put_invoice_invalid_project_id(ac_api_cookie, id, expected_status, error_msg):
    ac_api = AC_API(ac_api_cookie)
    payload = {}
    res = ac_api.update_invoice_configuration(id=id, payload=payload)
    res.assert_response_status(expected_status)
    assert res.json_response == error_msg


@pytest.mark.ac_api_uat
def test_put_invoice_empty_payload(new_project_invoice, ac_api_cookie):
    ac_api = AC_API(ac_api_cookie)

    res_get = ac_api.get_invoice_configuration(id=new_project_invoice)
    res_get.assert_response_status(200)

    res_get.json_response['configuredInvoice'] = True

    payload = {}
    res = ac_api.update_invoice_configuration(id=new_project_invoice, payload=payload)
    res.assert_response_status(200)

    assert res.json_response == res_get.json_response


def test_put_invoice_autoapprove_invoice(new_project_invoice, ac_api_cookie):
    ac_api = AC_API(ac_api_cookie)

    payload ={
      "autoApproveInvoice": 'true'
    }

    res = ac_api.update_invoice_configuration(id=new_project_invoice, payload=payload)
    res.assert_response_status(400)
    assert res.json_response =={
                                  "code": "MissingAutoApproveInvoiceBasedon",
                                  "message": "Missing auto approve invoice basedon"
                                }

@pytest.mark.ac_api_uat
def test_put_invoice_valid(new_project_invoice, ac_api_cookie):
    ac_api = AC_API(ac_api_cookie)

    payload = {
      "autoApproveInvoice": 'false',
      "autoApproveInvoiceBasedon": "TIME_SPENT",
      "autoGenerateInvoice": 'true',
      "autoGenerateInvoiceBasedon": "TIME_SPENT",
      "autoRejectInvoice": 'true',
      "configuredInvoice": 'true',
      "disableUserReportTime": 'true',
      "invoiceLineItemApproval": 'true',
      "projectInvoiceVarianceThreshold": 0,
      "requiresPMApproval": 'true'
    }

    res = ac_api.update_invoice_configuration(id=new_project_invoice, payload=payload)
    res.assert_response_status(200)
    updated_res = res.json_response

    get_res = ac_api.get_invoice_configuration(id=new_project_invoice)
    assert get_res.json_response == updated_res

