import os
import time

import allure
import pytest
from faker.generator import random

from adap.api_automation.utils.data_util import *
from adap.api_automation.utils.helpers import get_current_ip
from appen_connect.api_automation.services_config.ac_api import AC_API
from appen_connect.ui_automation.service_config.application import AC

pytestmark = [pytest.mark.regression_ac_core,  pytest.mark.regression_ac,pytest.mark.ac_ui_uat]

USER_NAME = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')


def add_ip_to_project(ip, project, ac_api_cookie_no_customer):
    api = AC_API(ac_api_cookie_no_customer)
    res = api.get_project_by_id(project)

    _payload = res.json_response
    _ips = _payload['allowedIps']
    _ips.append(ip)
    _payload['allowedIps'] = _ips

    res_update = api.update_project(project, _payload)
    res_update.assert_response_status(200)


@pytest.mark.ac_ui_smoke
# @pytest.mark.flaky(reruns=2)
def test_login_ac_vendor(app_test):
    user_name = get_user_email('test_active_vendor_account')
    password = get_user_password('test_active_vendor_account')
    app_test.ac_user.login_as(user_name=user_name, password=password)
    partial_username = user_name[0:27]
    app_test.verification.text_present_on_page(partial_username + "...")
    app_test.verification.link_is_displayed("Logout")


@pytest.mark.ac_ui_smoke
# @pytest.mark.flaky(reruns=2)
def test_login_as_raterlabs_employee(app_test):
    user_name = get_user_email('test_raterlabs_employee_account')
    password = get_user_password('test_raterlabs_employee_account')
    app_test.ac_user.login_as_raterlabs_user(user_name=user_name, password=password)
    partial_username = user_name[0:27]
    app_test.verification.text_present_on_page(partial_username + "...")
    app_test.verification.link_is_displayed("Logout")


@pytest.mark.skipif(pytest.env not in ["stage"], reason="Bug in QA env, ACE-13361")
@allure.issue("https://appen.atlassian.net/browse/ACE-13361", "BUG  on QA ACE-13361")
# @pytest.mark.flaky(reruns=2)
def test_login_as_facility_employee(app_test, ac_api_cookie_no_customer):
    user_name = get_user_email('test_facility_employee_account')
    password = get_user_password('test_facility_employee_account')
    project_id = get_test_data('test_facility_employee_account', 'project_id')

    app_test.ac_user.login_as_facility_user(user_name=user_name, password=password)

    if app_test.verification.wait_untill_text_present_on_the_page("You can only access the system from one of the permitted facilities.",
                                                                  max_time=2):
        add_ip_to_project(get_current_ip(), project_id, ac_api_cookie_no_customer)
        assert False
    else:
        partial_username = user_name[0:27]
        time.sleep(6)
        app_test.verification.text_present_on_page(partial_username + "...")
        app_test.verification.link_is_displayed("Logout")


@pytest.mark.ac_ui_uat
@allure.issue("https://appen.atlassian.net/browse/ACE-7852", "BUG ACE-7852")
@pytest.mark.skip(reason='ACE-7852')
# @pytest.mark.flaky(reruns=2)
def test_login_as_agency(app_test):
    user_name = get_user_email('test_agency_account')
    password = get_user_password('test_agency_account')
    app_test.ac_user.login_as_agency_user(user_name=user_name, password=password)
    partial_username = user_name[0:27]
    app_test.verification.text_present_on_page(partial_username + "...")
    app_test.verification.link_is_displayed("Logout")


@pytest.mark.ac_ui_smoke
# @pytest.mark.flaky(reruns=2)
def test_login_as_raterqualifications_user(app_test):
    user_name = get_user_email('test_rq_user_account')
    password = get_user_password('test_rq_user_account')
    app_test.ac_user.login_as_rq_user(user_name=user_name, password=password)
    partial_username = user_name[0:27]
    app_test.verification.text_present_on_page(partial_username + "...")
    app_test.verification.link_is_displayed("Logout")


@pytest.mark.ac_ui_smoke
# @pytest.mark.flaky(reruns=2)
def test_login_internal_ac_user(app_test):
    user_name = get_user_email('test_ui_account')
    password = get_user_password('test_ui_account')
    app_test.ac_user.login_as(user_name=user_name, password=password)
    partial_username = user_name[0:10]
    app_test.verification.text_present_on_page(partial_username)
    app_test.verification.link_is_displayed("Logout")


@pytest.mark.ac_ui_smoke
# @pytest.mark.flaky(reruns=2)
def test_login_internal_raterlabs_user(app_test):
    user_name = get_user_email('test_ui_account')
    password = get_user_password('test_ui_account')
    app_test.ac_user.login_as_raterlabs_user(user_name=user_name, password=password)
    partial_username = user_name[0:10]

    app_test.verification.text_present_on_page(partial_username)
    app_test.verification.link_is_displayed("Logout")


@pytest.mark.ac_ui_uat
@allure.issue("https://appen.atlassian.net/browse/ACE-7852", "BUG ACE-7852")
@pytest.mark.skip(reason='ACE-7852')
# @pytest.mark.flaky(reruns=2)
def test_login_internal_agency_user(app_test):
    user_name = get_user_email('test_ui_account')
    password = get_user_password('test_ui_account')
    app_test.ac_user.login_as_agency_user(user_name=user_name, password=password)
    partial_username = user_name[0:10]
    app_test.verification.text_present_on_page(partial_username)
    app_test.verification.link_is_displayed("Logout")


@pytest.mark.ac_ui_smoke
# @pytest.mark.flaky(reruns=2)
def test_login_internal_rq_user(app_test):
    user_name = get_user_email('test_ui_account')
    password = get_user_password('test_ui_account')
    app_test.ac_user.login_as_rq_user(user_name=user_name, password=password)
    partial_username = user_name[0:10]
    app_test.verification.text_present_on_page(partial_username)
    app_test.verification.link_is_displayed("Logout")


@pytest.mark.ac_ui_smoke
# @pytest.mark.flaky(reruns=2)
def test_login_internal_facility_user(app_test):
    user_name = get_user_email('test_ui_account')
    password = get_user_password('test_ui_account')
    app_test.ac_user.login_as_facility_user(user_name=user_name, password=password)
    partial_username = user_name[0:10]
    app_test.verification.text_present_on_page(partial_username)
    app_test.verification.link_is_displayed("Logout")