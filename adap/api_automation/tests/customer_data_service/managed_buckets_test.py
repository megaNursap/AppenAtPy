"""
Tests Customer Data Service internal endpoint /managed_buckets
"""
from adap.api_automation.services_config.akon import AkonUser
from adap.api_automation.services_config.customer_data_service import CDS
import pytest
import random
import json
from uuid import uuid4

from adap.api_automation.utils.data_util import get_test_data

mark_only_envs = pytest.mark.skipif(not pytest.running_in_preprod_subset, reason="Only enabled in preprod")
pytestmark = [pytest.mark.cds, pytest.mark.regression_core, mark_only_envs]

expected_keys = [
    'team_id',
    'bucket_name',
    'storage_provider_id',
    'created_at',
    'updated_at'
]


@pytest.fixture(scope='module')
def team_id():
    return uuid4().__str__()


@pytest.fixture(scope='module')
def bucket_data(team_id):
    storage_provider_ids = {
        'sandbox': 26,
        'integration': 26
    }
    data = {
        "team_id": team_id,
        "storage_provider_id": storage_provider_ids[pytest.env],
        "bucket_name": "test_bucket"
    }
    return data


@pytest.fixture(autouse=True, scope='module')
def teardown(adap_cds):
    yield
    adap_cds.delete_managed_bucket(team_id=team_id)


def test_get_all_managed_buckets(adap_cds):
    resp = adap_cds.get_all_managed_buckets()
    resp.assert_response_status(200)
    assert resp.json_response, "Response body is empty"
    assert isinstance(resp.json_response, list), '' \
                                                 f"Expecting array in response, got {type(resp.json_response)}"
    a_sample = random.choice(resp.json_response)
    assert all(map(lambda k: k in a_sample, expected_keys)), '' \
                                                             f"Expected keys: {expected_keys}" \
                                                             f"Actual keys: {list(a_sample.keys())}"


@pytest.mark.dependency()
def test_create_team_managed_bucket(team_id, bucket_data, adap_cds):
    # create a new bucket for the team
    resp = adap_cds.create_managed_bucket(data=bucket_data)
    resp.assert_response_status(201)
    assert resp.json_response, "Response body is empty"


@pytest.mark.dependency(depends=["test_create_team_managed_bucket"])
def test_get_team_managed_bucket(team_id, bucket_data, adap_cds):
    resp = adap_cds.get_team_managed_buckets(team_id=team_id)
    resp.assert_response_status(200)
    assert all(map(lambda k: k in resp.json_response, expected_keys)), '' \
                                                                       f"Expected keys: {expected_keys}" \
                                                                       f"Actual keys: {list(resp.json_response.keys())}"
    for key, e_val in bucket_data.items():
        a_val = resp.json_response.get(key)
        assert a_val == e_val, f"Key {key}, Expected: {e_val}, Actual: {a_val}"


@pytest.mark.dependency(depends=["test_get_team_managed_bucket"])
def test_update_team_managed_bucket(team_id, bucket_data, adap_cds):
    # update bucket for the team
    new_bucket_data = bucket_data.copy()
    new_bucket_data['bucket_name'] = 'f8-customer-data-sandbox'
    resp = adap_cds.update_managed_bucket(
        team_id=team_id,
        data=new_bucket_data)
    resp.assert_response_status(200)
    assert resp.json_response, "Response body is empty"
    # verify updated
    bucket = adap_cds.get_team_managed_buckets(team_id=team_id)
    bucket.assert_response_status(200)
    for key, e_val in new_bucket_data.items():
        a_val = bucket.json_response.get(key)
        assert a_val == e_val, f"Bucket data mismatch, expected: {e_val}, actual: {a_val}"


@pytest.mark.dependency(depends=["test_update_team_managed_bucket"])
def test_delete_team_managed_bucket(team_id, adap_cds):
    # delete bucket for the team
    resp = adap_cds.delete_managed_bucket(team_id=team_id)
    resp.assert_response_status(204)
    # verify not exists
    assert adap_cds.get_team_managed_buckets(team_id=team_id).status_code != 200, '' \
                                                                             f"Bucket hasn't been deleted"
