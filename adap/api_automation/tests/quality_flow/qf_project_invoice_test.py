"""
https://api-kepler.integration.cf3.us/project/swagger-ui/index.html#/Invoice%20Controller
"""

import pytest
from faker import Faker
import datetime

from adap.api_automation.services_config.quality_flow import QualityFlowApiProject
from adap.api_automation.utils.data_util import get_test_data, get_user_team_id

mark_env = pytest.mark.skipif(not pytest.running_in_preprod_integration, reason="for Integration env")

pytestmark = [pytest.mark.qf_api,
              pytest.mark.regression_qf,
              mark_env]

faker = Faker()

_today = datetime.datetime.now().strftime("%Y_%m_%d")

@pytest.fixture(scope="module")
def setup():
    username = get_test_data('qf_user', 'email')
    password = get_test_data('qf_user', 'password')
    default_project = get_test_data('qf_user', 'default_project')
    default_segmented_project = get_test_data('qf_user', 'default_segmented_project')
    team_id = get_user_team_id('qf_user')
    api = QualityFlowApiProject()
    cookies = api.get_valid_sid(username, password)
    print(cookies)
    return {
        "username": username,
        "password": password,
        "team_id": team_id,
        "api": api,
        "cookies": cookies,
        "default_project": default_project,
        "default_segmented_project": default_segmented_project
    }


def test_view_invoice_list_of_project_valid(setup):
    """
    1, user is able to view the invoice list of unit only project with valid data
    2, query invoice via startTime or endTime in unit only project
    3, query invoice via workerId in segmented project
    4, query invoice via status(SUCCESS) in unit only project
    5, query invoice via status(FATAL) in segmented project

    # query only support startTime or endTime or workerId or status(READY, IN_PROCESS, SUCCESS, ERROR, FATAL)
    """
    api = setup['api']
    project_id = setup['default_project']['id']
    default_segmented_project = setup['default_segmented_project']['id']
    team_id = setup['team_id']
    payload = {
        "pageNum": 1,
        "pageSize": 30,
        "query": "",          #query all kind of invoices
        # query only support startTime or endTime or workerId or status(READY, IN_PROCESS, SUCCESS, ERROR, FATAL)
        "statisticsType": "UNIT_COUNT"
    }
    # 1, query all invoices
    res = api.post_list_of_invoices(team_id, project_id, payload=payload)
    rsp = res.json_response
    assert rsp['code'] == 200
    assert rsp['message'] == "success"
    data = rsp.get('data')
    print(data)
    assert data is not None
    assert data['pageNumber'] == 1
    assert data['pageSize'] == 30
    assert data['totalPages'] is not None
    assert data['totalElements'] is not None

    # assert invoice content details
    content = data['content'][0]
    assert content is not None
    assert content['id'] is not None
    assert content['distributionId'] is None
    assert content['createdAt'] is not None
    assert content['status'] in ['READY', 'IN_PROCESS', 'SUCCESS', 'ERROR', 'FATAL']
    assert content['workerId'] is not None
    assert content['userEmail'] is not None
    assert content['payRate']
    assert content['workLoad'] is not None
    assert content['invoiceId'] is not None
    assert content['statisticsType'] in ['UNIT_COUNT', 'DURATIONS']
    assert content['startTime'] is not None
    assert content['endTime'] is not None
    assert content['externalProjectId'] is not None
    assert content['activeStatus'] is not None
    assert content['jobId'] is None
    assert content['jobTitle'] is None
    assert content['jobAlias'] is None
    assert content['version'] is not None


    # 2, query the invoices via workerId
    payload = {
        "pageNum": 1,
        "pageSize": 5,
        "query": "1297493",   #query the invoices via workerId
        "statisticsType": "UNIT_COUNT"
    }
    res = api.post_list_of_invoices(team_id, project_id, payload=payload)
    rsp = res.json_response
    assert rsp['code'] == 200
    assert rsp['message'] == "success"
    data = rsp.get('data')
    assert data is not None
    # assert invoice content details
    content = data['content'][0]
    assert content['id'] is not None
    assert content['status'] == 'SUCCESS'
    assert content['workerId'] is not None

    # # 3, query the invoices via startTime or endTime
    # payload = {
    #     "pageNum": 1,
    #     "pageSize": 5,
    #     "query": "2023-02-17T06:15:00Z",  #query the invoices via startTime or endTime -02-17 14:15:00   2023-02-17T06:15:00Z
    #     "statisticsType": "UNIT_COUNT"
    # }
    # res = api.post_list_of_invoices(team_id, project_id, payload=payload)
    # rsp = res.json_response
    # assert rsp['code'] == 200
    # assert rsp['message'] == "success"
    # data = rsp.get('data')
    # assert data is not None
    # # assert invoice content details
    # content = data['content'][0]
    # assert content['id'] is not None
    # assert content['status'] == 'FATAL'
    # assert content['workerId'] is not None


    # 4, query the invoices via status (SUCCESS)
    payload = {
        "pageNum": 1,
        "pageSize": 5,
        "query": "SUCCESS",   #query the invoices via status (SUCCESS)
        "statisticsType": "UNIT_COUNT"
    }
    res = api.post_list_of_invoices(team_id, project_id, payload=payload)
    rsp = res.json_response
    assert rsp['code'] == 200
    assert rsp['message'] == "success"
    data = rsp.get('data')
    assert data is not None
    # assert invoice content details
    content = data['content'][0]
    assert content['id'] is not None
    assert content['status'] == 'SUCCESS'
    assert content['workerId'] is not None

    # 5, query the invoices via status (FATAL)
    payload = {
        "pageNum": 1,
        "pageSize": 5,
        "query": "FATAL",   # query the invoices via status (FATAL)
        "statisticsType": "UNIT_COUNT"
    }
    res = api.post_list_of_invoices(team_id, project_id, payload=payload)
    rsp = res.json_response
    assert rsp['code'] == 200
    assert rsp['message'] == "success"
    data = rsp.get('data')
    assert data is not None
    # assert invoice content details
    content = data['content'][0]
    assert content['id'] is not None
    assert content['status'] == 'FATAL'
    assert content['workerId'] is not None

@pytest.mark.parametrize('name, team_id, message', [
    ('empty', '', 'Unauthorized'),
    ('not exist', 'fkreek0mvml', 'Access Denied'),
    ('other user', '45f42748-482b-4265-8a8c-73efa872b32b', 'Access Denied')
])
def test_view_invoice_list_of_project_invalid(setup, name, team_id, message):
    """
    user is unable to view the invoice list of project with valid data(invalid team_id)
    """
    api = setup['api']
    project_id = setup['default_project']['id']
    payload = {
        "pageNum": 1,
        "pageSize": 10,
        "query": "", #only support startTime or endTime or workerId or status(READY, IN_PROCESS, SUCCESS, ERROR, FATAL)
        "statisticsType": "UNIT_COUNT"
    }
    res = api.post_list_of_invoices(team_id, project_id, payload)
    assert res.status_code == 403
    assert res.json_response['message'] == message


def test_retry_single_fatal_invoice_to_fatal_valid(setup):
    """
    user is able to retry the fatal invoice of unit only project with valid data
    1. query the first FATAL invoice and assert the invoice
    2. retry the FATAL invoice and assert the invoice status update to READY
    3. Trigger the invoice batchJob to pickup the READY invoice record and send it to AC
    4. Wait and query the invoice list again to check status update to fatal
    """
    api = setup['api']
    project_id = setup['default_project']['id']
    team_id = setup['team_id']
    payload = {
        "pageNum": 1,
        "pageSize": 1,
        "query": "FATAL",   #query the workerId(integration+ez@figure-eight.com) to get his FATAL invoices
        "statisticsType": "UNIT_COUNT",
        "descending": False,
        "orderBy": "startTime"
    }

    # 1. query the one FATAL invoice
    res = api.post_list_of_invoices(team_id, project_id, payload=payload)
    rsp = res.json_response
    assert rsp['code'] == 200
    assert rsp['message'] == "success"
    data = rsp.get('data')
    assert data is not None
    content_list = data['content']
    assert len(content_list) == 1
    content = content_list[0]
    id = content['id']
    assert id is not None
    assert content['status'] == 'FATAL'
    assert content['userEmail'] is not None
    assert content['workerId'] is not None
    assert content['payRate'] is ''
    assert content['workLoad'] is not None
    assert content['jobTitle'] is None
    assert content['invoiceId'] is not None
    assert content['startTime'] is not None
    assert content['endTime'] is not None

    # 2. retry the FATAL invoice
    payload = [id]
    res = api.post_retry_of_invoices(team_id, project_id, payload=payload)
    rsp = res.json_response
    assert rsp['code'] == 200
    assert rsp['message'] == "success"
    data = rsp.get('data')
    assert data is not None
    # assert the one invoice data is correct
    invoice_data = data[0]
    invoice_order_id = invoice_data['id']
    assert invoice_order_id is not None
    assert invoice_data['status'] == 'READY'
    assert invoice_data['userEmail'] is not None
    assert invoice_data['workerId'] is not None
    assert invoice_data['payRate'] is ''
    assert invoice_data['workLoad'] is not None
    assert invoice_data['jobTitle'] is None
    assert invoice_data['invoiceId'] is not None
    assert content['startTime'] is not None
    assert content['endTime'] is not None

    #3. Trigger the invoice batchJob to retry send invoice to AC
    # batchjob id - ef77a010-75a9-48fa-b479-658847696b79
    # res = api.post_trigger_invoices('d48e5237-1ed9-4915-89bf-2e48e74236e6')
    # rsp = res.json_response
    # assert rsp['code'] ==200
    # time.sleep(65)

    # # Currently the project level batchjob will execute every hour, so can't verify this step except can trigger the batchjob via api request
    # #4. Wait and query the same invoice status become FATAL again
    # payload = {
    #     "pageNum": 1,
    #     "pageSize": 10,
    #     "descending": True,
    #     "orderBy": "status",
    #     "query": job_id,   #only support startTime or endTime or workerId or status(READY, IN_PROCESS, SUCCESS, ERROR, FATAL)
    #     "statisticsType": "UNIT_COUNT"
    # }
    # res = api.post_list_of_invoices(team_id, project_id, payload=payload)
    # rsp = res.json_response
    # assert rsp['code'] == 200
    # assert rsp['message'] == "success"
    # data = rsp.get('data')
    # assert data is not None
    # content = data['content']
    # assert content != []
    # is_found_the_retried_invoice_id = False
    # for invoice in content:
    #     if invoice['id'] == invoice_order_id:
    #         is_found_the_retried_invoice_id = True
    #         assert invoice['status'] == 'FATAL'
    #         break
    # # Check the batchjob pickup the invoice and send to AC get FATAL result
    # assert is_found_the_retried_invoice_id


def test_retry_multi_fatal_invoices_in_segmented_project_valid(setup):
    """
    user is able to retry the fatal invoice of segmented project with valid data
    1. query the two FATAL invoices and assert the invoice
    2. retry the two FATAL invoices and assert the invoices and assert status update to READY
    """
    api = setup['api']
    project_id = setup['default_segmented_project']['id']
    team_id = setup['team_id']
    payload = {
        "pageNum": 1,
        "pageSize": 2,
        "query": 'FATAL',  #prepared the user(integration+ez3@figure-eight.com) with >=2 FATAL invoices data
        "statisticsType": "UNIT_COUNT"
    }

    # 1. query two FATAL invoices
    res = api.post_list_of_invoices(team_id, project_id, payload=payload)
    rsp = res.json_response
    assert rsp['code'] == 200
    assert rsp['message'] == "success"
    data = rsp.get('data')
    assert data is not None
    assert len(data['content']) == 2
    ## assert first invoice content
    content1 = data['content'][0]
    assert content1 is not None
    id1 = content1['id']
    assert id1 is not None
    assert content1['status'] == 'FATAL'
    ## assert second invoice content
    content2 = data['content'][1]
    assert content2 is not None
    id2 = content2['id']
    assert id2 is not None
    assert content2['status'] == 'FATAL'

    # 2. retry the two FATAL invoices and assert status update to READY
    payload = [id1, id2]
    res = api.post_retry_of_invoices(team_id, project_id, payload=payload)
    rsp = res.json_response
    assert rsp['code'] == 200
    assert rsp['message'] == "success"
    data = rsp.get('data')
    assert data is not None
    assert len(data) == 2

    invoice1_data = data[0]
    assert invoice1_data['id'] is not None
    assert invoice1_data['status'] == 'READY'

    invoice2_data = data[1]
    assert invoice2_data['id'] is not None
    assert invoice2_data['status'] == 'READY'


def test_send_duplicated_retry_fatal_invoice_in_segmented_project_valid(setup):
    """
    send duplicated request for retry invoice in segmented project with valid data
    1. query the first FATAL invoice and assert the invoice
    2. retry the FATAL invoice and assert the invoice status update to READY
    3. send again for duplicated FATAL invoice
    """
    api = setup['api']
    project_id = setup['default_segmented_project']['id']
    team_id = setup['team_id']
    payload = {
        "pageNum": 1,
        "pageSize": 10,
        "query": '1298218',  #prepared the user(integration+ez4@figure-eight.com) with >=1 FATAL invoices data
        "statisticsType": "UNIT_COUNT"
    }

    # 1. query the one FATAL invoice
    res = api.post_list_of_invoices(team_id, project_id, payload=payload)
    rsp = res.json_response
    assert rsp['code'] == 200
    assert rsp['message'] == "success"
    data = rsp.get('data')
    assert data is not None
    content = data['content'][0]
    assert content != []
    id = content['id']
    assert id is not None
    assert content['status'] == 'FATAL'

    # 2. retry the FATAL invoice
    payload = [id]
    res1 = api.post_retry_of_invoices(team_id, project_id, payload=payload)
    # 3. resend the same retry requests and save as rsp2
    res2 = api.post_retry_of_invoices(team_id, project_id, payload=payload)
    rsp1 = res1.json_response
    rsp2 = res2.json_response

    # assert duplicated request send success and invoice status should keep READY
    assert rsp1['code'] == 200
    assert rsp1['message'] == "success"
    data1 = rsp1.get('data')
    assert data1 is not None
    assert len(data1) == 1
    invoice_data1 = data1[0]
    # assert the one invoice data is correct
    assert invoice_data1['id'] is not None
    assert invoice_data1['status'] == 'READY'
    assert invoice_data1['userEmail'] is not None

    assert rsp2['code'] == 200
    assert rsp2['message'] == "success"
    data2 = rsp2.get('data')
    assert data2 is not None
    assert len(data2) ==1
    # assert the one invoice data is correct
    invoice_data2 = data2[0]
    assert invoice_data2['id'] is not None
    assert invoice_data2['status'] == 'READY'
    assert invoice_data2['userEmail'] is not None

