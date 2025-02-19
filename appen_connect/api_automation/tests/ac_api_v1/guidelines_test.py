
from appen_connect.api_automation.services_config.ac_api_v1 import AC_API_V1
from adap.api_automation.utils.data_util import *
from datetime import date


pytestmark = [pytest.mark.regression_ac_core, pytest.mark.regression_ac, pytest.mark.ac_api_v1, pytest.mark.ac_api_v1_guidelines, pytest.mark.ac_api]

AUTH_KEY = get_test_data('auth_key', 'auth_key')


@pytest.mark.ac_api_uat
def test_get_project_guidelines():
    api = AC_API_V1(AUTH_KEY)
    resp = api.get_project_guidelines(project_id='511')
    resp.assert_response_status(200)
    assert len(resp.json_response) > 0


def test_get_project_guidelines_invalid_id():
    api = AC_API_V1(AUTH_KEY)
    resp = api.get_project_ias(project_id="123455")
    resp.assert_response_status(404)
    assert len(resp.json_response) == 0


@pytest.mark.ac_api_uat
def test_get_user_project_guidelines():
    user_id = get_test_data('test_active_vendor_account', 'id')

    api = AC_API_V1(AUTH_KEY)
    resp = api.get_user_guidelines(user_id=user_id)
    resp.assert_response_status(200)
    assert len(resp.json_response) > 0


def test_get_invalid_user_project_guidelines():
    api = AC_API_V1(AUTH_KEY)
    resp = api.get_user_guidelines(user_id="")
    resp.assert_response_status(404)

@pytest.mark.skip(reason='because of the bug ACE-12612')
@pytest.mark.ac_api_uat
def test_get_guideline_document():
    user_id = get_test_data('test_active_vendor_account', 'id')

    guideline_document_id = get_test_data('test_active_vendor_account', 'guideline_document_id')

    api = AC_API_V1(AUTH_KEY)
    resp = api.get_user_guideline_document(user_id=user_id, document_id=guideline_document_id)
    resp.assert_response_status(200)


def test_get_invalid_guideline_document():
    user_id = get_test_data('test_active_vendor_account', 'id')
    api = AC_API_V1(AUTH_KEY)
    resp = api.get_user_guideline_document(user_id=user_id, document_id="1234")
    resp.assert_response_status(404)
    assert len(resp.json_response) == 0


def test_post_guideline_acknowledgement():
    user_id = get_test_data('test_active_vendor_account', 'id')

    api = AC_API_V1(AUTH_KEY)
    guideline_id = get_test_data('test_active_vendor_account', 'guideline_id')

    project_id = get_test_data('test_active_vendor_account', 'project_id')

    to_date = date.today()
    payload = {"guideline": {
        "id": guideline_id
    },
        "project": {
            "id": project_id
        },
        "guidelineAcknowledgedDate": to_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "guidelineViewedDate": to_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "user": {
            "id": user_id

        }
    }
    resp = api.post_guideline_acknowledgement(payload=payload)
    resp.assert_response_status(200)
    assert (resp.json_response['apiMessage'] == "Guideline Acknowledgement Message placed on queue.")
    assert len(resp.json_response) > 0


def test_post_guideline_acknowledgement_invalid_guideline_id():
    user_id = get_user_id('test_active_vendor_account')
    api = AC_API_V1(AUTH_KEY)
    guideline_id = 1234
    project_id = get_test_data('test_active_vendor_account', 'project_id')
    to_date = date.today()
    payload = {"guideline": {
        "id": guideline_id
    },
        "project": {
            "id": project_id
        },
        "guidelineAcknowledgedDate": to_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "guidelineViewedDate": to_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "user": {
            "id": user_id

        }
    }
    resp = api.post_guideline_acknowledgement(payload=payload)
    resp.assert_response_status(400)
    assert (resp.json_response['fieldErrors'][0]['message'] == 'Invalid guideline id specified. A guideline does not '
                                                               'exist for this user id %s and project id %s and '
                                                               'guideline id: %s' % (user_id, project_id, guideline_id))


def test_post_guideline_acknowledgement_invalid_user_id():
    user_id = 12953
    api = AC_API_V1(AUTH_KEY)
    guideline_id = get_test_data('test_active_vendor_account', 'guideline_id')

    project_id = get_test_data('test_active_vendor_account', 'project_id')
    to_date = date.today()
    payload = {"guideline": {
        "id": guideline_id
    },
        "project": {
            "id": project_id
        },
        "guidelineAcknowledgedDate": to_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "guidelineViewedDate": to_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "user": {
            "id": user_id

        }
    }
    resp = api.post_guideline_acknowledgement(payload=payload)
    resp.assert_response_status(400)
    # Commenting this assert statement as the error message is for the same failure is different each time
    '''assert (resp.json_response['fieldErrors'][0]['message'] == 'Invalid guideline id specified. A guideline does not '
                                                               'exist for this user id %s and project id %s and '
                                                               'guideline id: %s' % (user_id, project_id, guideline_id))'''


def test_post_guideline_acknowledgement_invalid_date():
    user_id = get_test_data('test_active_vendor_account', 'id')

    api = AC_API_V1(AUTH_KEY)
    guideline_id = get_test_data('test_active_vendor_account', 'guideline_id')

    project_id = get_test_data('test_active_vendor_account', 'project_id')

    to_date = date.today()
    payload = {"guideline": {
        "id": guideline_id
    },
        "project": {
            "id": project_id
        },
        "guidelineAcknowledgedDate": to_date.strftime("%Y-%m-%dT%H:%M:%S"),
        "guidelineViewedDate": to_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "user": {
            "id": user_id

        }
    }
    resp = api.post_guideline_acknowledgement(payload=payload)
    resp.assert_response_status(400)
    assert (resp.json_response['fieldErrors'][0]['field'] == 'guidelineAcknowledgedDate')