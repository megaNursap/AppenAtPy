import pytest
from faker import Faker

from adap.api_automation.services_config.akon import AkonUser
from adap.api_automation.services_config.management import Management
from adap.api_automation.utils.data_util import generate_random_string
from adap.api_automation.utils.data_util import get_user_api_key, get_user_team_id, get_user_email, \
    get_user_org_id, get_test_data

mark_only_fed = pytest.mark.skipif(pytest.env != "fed", reason="Only fed has this feature in use")
pytestmark = [pytest.mark.fed_api_smoke,  mark_only_fed]


@pytest.fixture(scope="module")
def _user_info():
    api_key = get_user_api_key('org_admin')
    admin_email = get_user_email('org_admin')
    teams_id = get_user_team_id('org_admin')
    org_id = get_user_org_id('org_admin')
    multi_team_user = get_user_team_id('multi_team_user')[0]
    faker = Faker()
    user_name = (faker.name() + faker.zipcode()).replace(' ', '')
    new_email = "{env}+{user_name}@appen.com".format(env=pytest.env, user_name=user_name)
    return {
        "email": new_email,
        "firstName": user_name,
        "lastName": "API_TEST",
        "org_admin_api_key": api_key,
        "org_admin_email": admin_email,
        "teams": teams_id,
        "wrong_team": multi_team_user,
        "org_id": org_id
    }


@pytest.mark.dependency()
@pytest.mark.management_api
@pytest.mark.fed_api
def test_create_user(_user_info):
    payload = {
          'email': _user_info['email'],
          'firstName': _user_info['firstName'],
          'lastName': _user_info['lastName'],
          'teamId': _user_info['teams']
    }
    new_user_res = Management(_user_info['org_admin_api_key']).create_user(payload)
    new_user_res.assert_response_status(204)


@pytest.mark.management_api
@pytest.mark.fed_api
def test_create_user_invalid_api_key(_user_info):
    payload = {
          'email': _user_info['email'],
          'firstName': _user_info['firstName'],
          'lastName': _user_info['lastName'],
          'teamId': _user_info['teams']
    }
    new_user_res = Management(_user_info['org_admin_api_key'][:-1]).create_user(payload)
    new_user_res.assert_response_status(403)
    assert new_user_res.text == 'User does not exist'


@pytest.mark.management_api
@pytest.mark.fed_api
def test_create_user_invalid_email_format(_user_info):
    payload = {
        'email': _user_info['email'][:-3],
        'firstName': _user_info['firstName'],
        'lastName': _user_info['lastName'],
        'teamId': _user_info['teams']
    }

    new_user_res = Management(_user_info['org_admin_api_key']).create_user(payload)
    new_user_res.assert_response_status(400)
    print(new_user_res.json_response)
    assert "email must be a well-formed email address" in new_user_res.json_response.get('errors')


@pytest.mark.management_api
@pytest.mark.fed_api
def test_create_user_email_is_taken(_user_info):
    payload = {
        'email': _user_info['org_admin_email'],
        'firstName': _user_info['firstName'],
        'lastName': _user_info['lastName'],
        'teamId': _user_info['teams']
    }
    new_user_res = Management(_user_info['org_admin_api_key']).create_user(payload)
    new_user_res.assert_response_status(403)
    # assert new_user_res.text == 'Could not create user'


@pytest.mark.management_api
@pytest.mark.fed_api
def test_create_user_no_email(_user_info):
    payload = {
        'email': "",
        'firstName': _user_info['firstName'],
        'lastName': _user_info['lastName'],
        'teamId': _user_info['teams']
    }
    new_user_res = Management(_user_info['org_admin_api_key']).create_user(payload)
    new_user_res.assert_response_status(400)
    assert 'email must not be blank' in new_user_res.json_response.get('errors')


@pytest.mark.management_api
@pytest.mark.fed_api
def test_create_user_no_first_name(_user_info):
    payload = {
        'email': _user_info['email'],
        'firstName': "",
        'lastName': "API",
        'teamId': _user_info['teams']
    }
    new_user_res = Management(_user_info['org_admin_api_key']).create_user(payload)
    new_user_res.assert_response_status(400)
    assert 'firstName must not be blank' in new_user_res.json_response.get('errors')


# recent change https://appen.atlassian.net/browse/DED-1869?focusedCommentId=409803 lastname is not mandatory
@pytest.mark.management_api
@pytest.mark.fed_api
def test_create_user_no_last_name(_user_info):
    payload = {
        'email': ("new"+_user_info['email']),
        'firstName': "firstname",
        'lastName': "",
        'teamId': _user_info['teams']
     }
    new_user_res = Management(_user_info['org_admin_api_key']).create_user(payload)
    new_user_res.assert_response_status(204)


@pytest.mark.management_api
@pytest.mark.fed_api
def test_create_user_no_team_id(_user_info):
    payload = {
        'email': _user_info['email'],
        'firstName': _user_info['firstName'],
        'lastName': "API",
        'teamId': ""
    }
    new_user_res = Management(_user_info['org_admin_api_key']).create_user(payload)
    new_user_res.assert_response_status(400)
    assert 'teamId must not be blank' in new_user_res.json_response.get('errors')


@pytest.mark.management_api
@pytest.mark.fed_api
def test_create_user_invalid_team_id(_user_info):
    payload = {
        'email': _user_info['email'],
        'firstName': _user_info['firstName'],
        'lastName': "API",
        'teamId': _user_info['teams'][:-1]
    }
    new_user_res = Management(_user_info['org_admin_api_key']).create_user(payload)
    new_user_res.assert_response_status(403)
    assert new_user_res.text == 'Team does not exist'


# BUG, user is able to create new account for team which is not part of his org
# bug fixed, user is not able to create new account for team(get_user_team_id('non_cf_team')) which
# is not in his org, return 403
@pytest.mark.management_api
def test_create_user_team_not_in_org(_user_info):
    payload = {
        'email': _user_info['email'],
        'firstName': _user_info['firstName'],
        'lastName': "API",
        'teamId': get_user_team_id('test_account')
    }
    new_user_res = Management(_user_info['org_admin_api_key']).create_user(payload)
    new_user_res.assert_response_status(403)


#  user already team admin, api returns 403? Bug filed and resolved
# https://appen.atlassian.net/browse/DED-1878 filed
@pytest.mark.dependency(depends=["test_create_user"])
@pytest.mark.management_api
@pytest.mark.fed_api
def test_make_user_team_admin(_user_info):
    user_email = _user_info['email']
    new_user_res = Management(_user_info['org_admin_api_key']).make_user_team_admin(user_email)
    new_user_res.assert_response_status(204)


# even api successful, I do not see team admin permission is revoked, on UI, it also says
#  there was an error updating member role
# https://appen.atlassian.net/browse/DED-1879 filed
#  for user in cf_internal team, not able to revoke the permission
@pytest.mark.dependency(depends=["test_create_user", "test_make_user_team_admin"])
@pytest.mark.management_api
def test_revoke_user_team_admin(_user_info):
    user_email = _user_info['email']
    new_user_res = Management(_user_info['org_admin_api_key']).revoke_user_team_admin_access(user_email)
    new_user_res.assert_response_status(204)


@pytest.mark.dependency(depends=["test_create_user"])
@pytest.mark.management_api
def test_make_user_org_admin(_user_info):
    user_email = _user_info['email']
    new_user_res = Management(_user_info['org_admin_api_key']).make_user_org_admin(user_email)
    new_user_res.assert_response_status(204)


@pytest.mark.dependency(depends=["test_create_user", "test_make_user_org_admin"])
@pytest.mark.management_api
def test_revoke_user_org_admin(_user_info):
    user_email = _user_info['email']
    new_user_res = Management(_user_info['org_admin_api_key']).revoke_user_org_admin_access(user_email)
    new_user_res.assert_response_status(204)


@pytest.mark.dependency(depends=["test_create_user"])
@pytest.mark.management_api
@pytest.mark.skip
def test_move_user_to_team(_user_info):
    user_email = _user_info['email']
    new_team = _user_info['teams'][1]
    jwt_token = get_test_data('org_admin', 'jwt_token')
    res = Management(_user_info['org_admin_api_key']).move_user_to_team(user_email, new_team)
    res.assert_response_status(204)
    org = _user_info['org_id']
    akon = AkonUser(get_user_api_key('org_admin'), jwt_token)
    assert akon.user_belongs_to_team(user_email, new_team, org)
    assert not akon.user_belongs_to_team(user_email, _user_info['teams'][0], org)


# BUG, user is able to move to the team in other org
@pytest.mark.dependency(depends=["test_create_user"])
@pytest.mark.management_api
@pytest.mark.skip
def test_move_user_to_other_org(_user_info):
    user_email = _user_info['email']
    new_team = get_user_team_id('non_cf_team')
    res = Management(_user_info['org_admin_api_key']).move_user_to_team(user_email, new_team)
    res.assert_response_status(403)
    print("text is:", res.text)
    print("header is:", res.headers)


@pytest.mark.management_api
@pytest.mark.fed_api
def test_disable_user_invalid_email(_user_info):
    user_email = _user_info['email']
    new_user_res = Management(_user_info['org_admin_api_key']).disable_user("not_exist"+user_email)
    new_user_res.assert_response_status(403)


@pytest.mark.dependency(depends=["test_create_user"])
@pytest.mark.management_api
@pytest.mark.fed_api
def test_disable_user(_user_info):
    user_email = _user_info['email']
    new_user_res = Management(_user_info['org_admin_api_key']).disable_user(user_email)
    new_user_res.assert_response_status(204)


@pytest.mark.dependency(depends=["test_create_user"])
@pytest.mark.management_api
@pytest.mark.fed_api
def test_update_user_attributes(_user_info):
    user_email = _user_info['email']
    new_payload = {
        "email": ("updated"+_user_info['email']),
        "firstName": "Updated First Name",
        "lastName": "Updated Last Name"
    }
    new_user_res = Management(_user_info['org_admin_api_key']).update_user_attributes(user_email, new_payload)
    new_user_res.assert_response_status(200)


@pytest.mark.dependency(depends=["test_create_user","test_update_user_attributes"])
@pytest.mark.management_api
@pytest.mark.fed_api
def test_update_user_invalid_email(_user_info):
    user_email = _user_info['email']
    new_payload = {
        "email": ("updated"+_user_info['email'][:-3]),
        "firstName": "Updated First Name",
        "lastName": "Updated Last Name"
    }
    new_user_res = Management(_user_info['org_admin_api_key']).update_user_attributes(("updated"+user_email), new_payload)
    new_user_res.assert_response_status(400)


# https://appen.atlassian.net/browse/QED-2132, for token in header, users need to have cf_internal role
@pytest.mark.management_api
@pytest.mark.fed_api
@pytest.mark.skip(reason='Issue DED-2356')
def test_create_userless_team_mandatory_fields():
    team_name = "userless team" + generate_random_string()
    payload = {
        "name": team_name
     }
    new_team_res = Management(get_user_api_key('cf_internal_role')).create_userless_team(payload)
    new_team_res.assert_response_status(201)
    assert len(new_team_res.json_response.get('id')) > 0
    assert new_team_res.json_response.get('name') == team_name
    assert new_team_res.json_response.get('markup') == 20
    assert new_team_res.json_response.get('max_running_jobs') == 30
    assert new_team_res.json_response.get('project_number') == "PN1101"
    assert new_team_res.json_response.get('plan') == "enterprise"
    assert not new_team_res.json_response.get('design_verified')
    assert new_team_res.json_response.get('additional_roles_names') == []
    assert not new_team_res.json_response.get('smart_validators')
    if pytest.env == "fed":
        assert new_team_res.json_response.get('requester_render_js')
        assert new_team_res.json_response.get('assisted_image_transcription')
    else:
        assert not new_team_res.json_response.get('requester_render_js')
        assert not new_team_res.json_response.get('assisted_image_transcription')


@pytest.mark.management_api
@pytest.mark.fed_api
@pytest.mark.skip(reason='Issue DED-2356')
def test_create_userless_team_invalid_token(_user_info):
    payload = {
        "name": "Testing Automation Userless Team API",
    }
    new_team_res = Management(_user_info['org_admin_api_key']).create_userless_team(payload)
    new_team_res.assert_response_status(403)


@pytest.mark.management_api
@pytest.mark.fed_api
@pytest.mark.skip(reason='Issue DED-2356')
def test_create_userless_team_missing_required_fields():
    payload = {
        "name": ""
    }
    new_team_res = Management(get_user_api_key('cf_internal_role')).create_userless_team(payload)
    new_team_res.assert_response_status(400)
    assert new_team_res.json_response.get('data') == None
    assert new_team_res.json_response.get('errors') == ['name must not be blank']


@pytest.mark.management_api
@pytest.mark.fed_api
@pytest.mark.skip(reason='Issue DED-2356')
@pytest.mark.parametrize('case_desc, project_number, plan, markup, max_running_jobs, '
                         'requester_render_js, design_verified, smart_validators, '
                         'assisted_image_transcription, taxonomyzer_client, expected_status',
                         [
                           ("admin project plan", "PN123", "admin", 15, 20, True, True, True, True, True, 201),
                           ("enterprise project plan", "PN123", "enterprise", 15, 20, True, False, True, False, True, 201),
                           ("trial project plan", "PN123", "trial", 15, 20, False, False, True, False, True, 201),
                           ("data_for_everyone project plan", "PN123", "data_for_everyone", 15, 20, False, False, True, False, True, 201),
                          ])
def test_create_userless_team_various_input(case_desc, project_number, plan, markup, max_running_jobs,
                                            requester_render_js, design_verified, smart_validators,
                                            assisted_image_transcription, taxonomyzer_client, expected_status):
    team_name = "userless team" + generate_random_string()
    payload = {
        "name": team_name,
        "project_number": project_number,
        "plan": plan,
        "markup": markup,
        "max_running_jobs": max_running_jobs,
        "requester_render_js": requester_render_js,
        "design_verified": design_verified,
        "smart_validators": smart_validators,
        "assisted_image_transcription": assisted_image_transcription,
        "taxonomyzer_client": taxonomyzer_client
    }
    new_team_res = Management(get_user_api_key('cf_internal_role')).create_userless_team(payload)
    new_team_res.assert_response_status(expected_status)
    assert len(new_team_res.json_response.get('id')) > 0
    assert new_team_res.json_response.get('name') == team_name
    assert new_team_res.json_response.get('markup') == markup
    assert new_team_res.json_response.get('max_running_jobs') == max_running_jobs
    if plan == "trial":
        assert new_team_res.json_response.get('project_number') == "PN1101"
    elif plan == "data_for_everyone":
        assert new_team_res.json_response.get('project_number') == "PN143"
    else:
        assert new_team_res.json_response.get("project_number") == project_number
    assert new_team_res.json_response.get('plan') == plan
    assert new_team_res.json_response.get('design_verified') == design_verified
    assert new_team_res.json_response.get('additional_roles_names') == ['taxonomyzer_client']
    assert new_team_res.json_response.get('smart_validators') == smart_validators
    assert new_team_res.json_response.get('requester_render_js') == requester_render_js
    assert new_team_res.json_response.get('assisted_image_transcription') == assisted_image_transcription
