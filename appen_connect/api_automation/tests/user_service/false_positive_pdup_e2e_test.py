'''
#These APIs {{GATEWAY}}/test-maas-pdup/** is removed and not valid anymore
import time
import allure
import pytest

from adap.api_automation.utils.data_util import get_test_data, find_dict_in_array_by_value
from appen_connect.api_automation.services_config.ac_user_service import UserService
from appen_connect.api_automation.services_config.pdup import AC_PDUP_API


mark_only_envs = pytest.mark.skipif(
    pytest.env not in ["stage"],
    reason="Only AC Stage enabled feature")


# Removed markers due to ACE-17177, gateway service has been deprecated
# pytestmark = [pytest.mark.pdup, pytest.mark.regression_ac_user_service, mark_only_envs]

vendor1 = get_test_data('false_positive_pdup1', 'id')
vendor2 = get_test_data('false_positive_pdup2', 'id')

API_USER_SERVICE = UserService()
API_PDUP = AC_PDUP_API()

payload_pdup_vendor1 = {
    "worker_id": vendor1,
    "max_user_count": 200,
    "sort": "desc",
    "exclude": [],
    "include_false_positives": 'true'
}


def set_up_false_positive_status(ac_api_cookie, workers, status):
    for worker_id in workers:
        res = API_USER_SERVICE.get_false_positive_by_user(user_id=worker_id, cookies=ac_api_cookie)
        res.assert_response_status(200)

        for record in res.json_response:
            if record['isFalsePositive'] != status:
                payload = {
                    "id": record['id'],
                    "userId": record['userId'],
                    "duplicateUserId": record['duplicateUserId'],
                    "attribute": record['attribute'],
                    "isFalsePositive": status
                }
                update_res = API_USER_SERVICE.put_false_positive_by_user(payload=payload, cookies=ac_api_cookie)
                assert update_res.status_code == 200, 'Not able to update falsepositive status for {} {}'.format(
                    record['userId'], record['attribute'])


@pytest.fixture(scope='module', autouse=True)
def set_up_test_data(ac_api_cookie):
    set_up_false_positive_status(ac_api_cookie, workers=[vendor1, vendor2], status=False)
    yield
    set_up_false_positive_status(ac_api_cookie, workers=[vendor1, vendor2], status=False)


@pytest.mark.dependency()
@allure.issue("https://appen.atlassian.net/browse/ACE-17177", 'Bug: ACE-17177')
def test_initial_status_for_vendor(ac_api_cookie):

    pdup_res = API_PDUP.post_check_pdup(payload_pdup_vendor1, cookies=ac_api_cookie)
    pdup_res.assert_response_status(200)

    total = pdup_res.json_response['total']
    num_of_matched_users = pdup_res.json_response['num_of_matched_users']
    num_of_false_positives = pdup_res.json_response['num_of_false_positives']

    assert total == num_of_matched_users + num_of_false_positives

    pdup_workers = pdup_res.json_response['potential_duplicates']
    false_positive_workers = pdup_res.json_response['false_positives']

    assert pdup_res.json_response['reference_worker_id'] == vendor1
    assert num_of_matched_users == len(pdup_workers)
    assert not false_positive_workers and num_of_false_positives == 0

    matched_vendor = find_dict_in_array_by_value(pdup_workers, 'user_id', vendor2)
    assert matched_vendor
    assert matched_vendor['user_id'] == vendor2
    assert len(matched_vendor['matched_attributes']) >= 2
    assert find_dict_in_array_by_value(matched_vendor['matched_attributes'], 'attribute', 'address')


@pytest.mark.dependency(depends=["test_initial_status_for_vendor"])
def test_mark_vendor_as_false_positive(ac_api_cookie):
    # find falsepositive record for vendor1 for attribute address and vendor2
    res_check_worker = API_USER_SERVICE.get_false_positive_by_user(vendor1, cookies=ac_api_cookie)
    res_check_worker.assert_response_status(200)

    _record = None
    for record in res_check_worker.json_response:
        if record['duplicateUserId'] == vendor2 and record['attribute'] == 'address':
            _record = record
            break

    if _record:   #  update record
        payload = {
            "id": _record['id'],
            "userId": vendor1,
            "duplicateUserId": vendor2,
            "attribute": 'address',
            "isFalsePositive": 'true'
        }
        res = API_USER_SERVICE.put_false_positive_by_user(payload, cookies=ac_api_cookie)
        res.assert_response_status(200 )
    else: #  POST new record
        payload = {
            "userId": vendor1,
            "duplicateUserId": vendor2,
            "attribute": "address",
            "isFalsePositive": 'true'
        }

        res = API_USER_SERVICE.post_false_positive_by_user(payload, cookies=ac_api_cookie)
        res.assert_response_status(200)

    time.sleep(5)

    pdup_res = API_PDUP.post_check_pdup(payload_pdup_vendor1, cookies=ac_api_cookie)
    pdup_res.assert_response_status(200)

    total = pdup_res.json_response['total']
    num_of_matched_users = pdup_res.json_response['num_of_matched_users']
    num_of_false_positives = pdup_res.json_response['num_of_false_positives']

    assert total == num_of_matched_users + num_of_false_positives
    assert num_of_false_positives > 0

    pdup_workers = pdup_res.json_response['potential_duplicates']
    false_positive_workers = pdup_res.json_response['false_positives']
    assert num_of_matched_users == len(pdup_workers)
    assert num_of_false_positives == len(false_positive_workers)

    _false_positive_vendor2 = find_dict_in_array_by_value(false_positive_workers, 'user_id', vendor2)
    assert _false_positive_vendor2
    assert _false_positive_vendor2['matched_attributes'] == [
                                                              {
                                                                "attribute": "address",
                                                                "value": "697-4889 Donec Av.",
                                                                "match": True
                                                              },
                                                              {
                                                                "attribute": "emails",
                                                                "value": "sandbox+vpn00004@figure-eight.com",
                                                                "match": True
                                                              }
                                                            ]


@pytest.mark.dependency(depends=["test_mark_vendor_as_false_positive"])
def test_mark_vendor_as_not_false_positive(ac_api_cookie):
    res_check_worker = API_USER_SERVICE.get_false_positive_by_user(vendor1, cookies=ac_api_cookie)
    res_check_worker.assert_response_status(200)

    _record = None
    for record in res_check_worker.json_response:
        if record['duplicateUserId'] == vendor2 and record['attribute'] == 'address':
            _record = record
            break

    assert _record, "falsePositive record has not been found"

    payload = {
        "id": _record['id'],
        "userId": vendor1,
        "duplicateUserId": vendor2,
        "attribute": 'address',
        "isFalsePositive": 'false'
    }
    res = API_USER_SERVICE.put_false_positive_by_user(payload, cookies=ac_api_cookie)
    res.assert_response_status(200)
    time.sleep(5)

    # check pdup data
    pdup_res = API_PDUP.post_check_pdup(payload_pdup_vendor1, cookies=ac_api_cookie)
    pdup_res.assert_response_status(200)

    false_positive_workers = pdup_res.json_response['false_positives']
    if false_positive_workers: #  if there are any falsepositive workers - verify vendor2 is not part of this list
        _false_positive_vendor2 = find_dict_in_array_by_value(false_positive_workers, 'user_id', vendor2)
        assert not _false_positive_vendor2

'''