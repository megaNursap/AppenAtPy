import allure
import pytest

from adap.api_automation.utils.data_util import get_test_data, find_dict_in_array_by_value
from appen_connect.api_automation.services_config.pdup import AC_PDUP_API

mark_only_envs = pytest.mark.skipif(
    pytest.env not in ["stage"],
    reason="Only AC Stage enabled feature")

# Removed markers due to ACE-17177, gateway service has been deprecated
# pytestmark = [pytest.mark.pdup, pytest.mark.regression_ac_user_service, pytest.mark.ac_fraud_detection, mark_only_envs]


def jaccard_similarity(x, y):
    """ returns the jaccard similarity between two lists """
    intersection_cardinality = len(set.intersection(*[set(x), set(y)]))
    union_cardinality = len(set.union(*[set(x), set(y)]))
    return intersection_cardinality / float(union_cardinality)


@allure.issue("https://appen.atlassian.net/browse/ACE-17177", 'Bug: ACE-17177')
def test_pdup_healthcheck(ac_api_cookie):
    pdup_res = AC_PDUP_API().get_pdup_healthcheck(cookies=ac_api_cookie)
    assert pdup_res.status_code == 200
    assert pdup_res.json_response['status'] == 'pass'
    assert pdup_res.json_response['app-name'] == 'Potential Duplicates Service'


@allure.issue("https://appen.atlassian.net/browse/ACE-17177", 'Bug: ACE-17177')
def test_pdup_required_fields_response(ac_api_cookie):
    api_pdup = AC_PDUP_API(cookies=ac_api_cookie)
    worker = get_test_data('citiverify', 'id')
    pdup_res = api_pdup.get_check_pdup_by_worker_id(worker_id=worker)

    expected_fields = [
        'reference_worker_id',
        'similarity_score',
        'total',
        'num_of_matched_users',
        'num_of_false_positives',
        'potential_duplicates'
    ]
    assert all(map(lambda k: k in pdup_res.json_response, expected_fields)), '' \
                                                                             f"Expected keys: {expected_fields}" \
                                                                             f"Actual keys: {list(pdup_res.json_response.keys())}"

@allure.issue("https://appen.atlassian.net/browse/ACE-17177", 'Bug: ACE-17177')
def test_pdup_full_name(ac_api_cookie):
    worker = get_test_data('fraud_detection', 'check_ip_us_no_vpn')
    api_pdup = AC_PDUP_API(cookies=ac_api_cookie)
    pdup_res = api_pdup.get_check_pdup_by_worker_id(worker_id=worker)

    assert pdup_res.status_code == 200
    assert str(pdup_res.json_response['reference_worker_id']) == worker
    # at least 1 match by full name should exist
    # by default get returns 10 records, if no matches by full_name -> try post request

    found_full_name_match = False
    for matched_vendor in pdup_res.json_response['potential_duplicates']:
        for matched_attribute in matched_vendor['matched_attributes']:
            if found_full_name_match: break
            if matched_attribute['attribute'] == 'full_name':
                found_full_name_match = True
                vendor_full_name = matched_vendor['attributes']['first_name'] + matched_vendor['attributes'][
                    'last_name']
                assert jaccard_similarity(matched_attribute['value'], vendor_full_name) > 0.7

    # POST returns max  number of records based on max_user_count param
    if not found_full_name_match:
        payload_pdup_vendor1 = {
            "worker_id": worker,
            "max_user_count": 200,
            "sort": "desc",
            "exclude": [],
            "include_false_positives": 'true'
        }
        pdup_res = api_pdup.post_check_pdup(payload_pdup_vendor1, cookies=ac_api_cookie)
        assert pdup_res.status_code == 200
        assert str(pdup_res.json_response['reference_worker_id']) == worker

        for matched_vendor in pdup_res.json_response['potential_duplicates']:
            for matched_attribute in matched_vendor['matched_attributes']:
                if found_full_name_match: break
                if matched_attribute['attribute'] == 'full_name':
                    found_full_name_match = True
                    vendor_full_name = matched_vendor['attributes']['first_name'] + matched_vendor['attributes'][
                        'last_name']
                    assert jaccard_similarity(matched_attribute['value'], vendor_full_name) > 0.7

    assert found_full_name_match, 'Duplication by full name has not been found'


@pytest.mark.skip("Not working; not in real time")
def test_pdup_address_duplication(ac_api_cookie):
    worker = get_test_data('fraud_detection', 'duplication_address')
    api_pdup = AC_PDUP_API(cookies=ac_api_cookie)

    payload_pdup_vendor1 = {
        "worker_id": worker[0],
        "max_user_count": 200,
        "sort": "desc",
        "exclude": [],
        "include_false_positives": 'true'
    }
    pdup_res = api_pdup.post_check_pdup(payload_pdup_vendor1, cookies=ac_api_cookie)
    assert pdup_res.status_code == 200
    assert str(pdup_res.json_response['reference_worker_id']) == worker[0]

    potential_duplicates = pdup_res.json_response['potential_duplicates']

    vendor_duplicate = find_dict_in_array_by_value(potential_duplicates, 'user_id', int(worker[1]))

    found_address_match = False

    for matched_attribute in vendor_duplicate['matched_attributes']:
        if found_address_match: break
        if matched_attribute['attribute'] == 'address':
            found_address_match = True
            assert jaccard_similarity(matched_attribute['value'], vendor_duplicate['address']) > 0.7

    assert found_address_match, 'Duplication by address has not been found'
