import pytest
from faker import Faker
from selenium.common import NoSuchElementException

from adap.api_automation.utils.data_util import get_test_data

faker = Faker()

mark_env = pytest.mark.skipif(not pytest.running_in_preprod_integration, reason="for Integration env")
pytestmark = [pytest.mark.qf_ui,
              pytest.mark.regression_qf,
              pytest.mark.qf_uat_ui,
              mark_env]
icm_email = faker.email()
icm_name = faker.name()


@pytest.fixture(scope="module")
def qf_login(app):
    username = get_test_data('qf_user_ui', 'email')
    password = get_test_data('qf_user_ui', 'password')

    app.user.login_as_customer(username, password)
    app.driver.implicitly_wait(10)


@pytest.fixture(scope="function")
def qf_refresh_page(app):
    app.navigation.refresh_page()
    app.driver.implicitly_wait(10)


@pytest.mark.regression_qf
@pytest.mark.qf_ui_smoke
def test_add_contributor_ui_elements(app, qf_login, qf_refresh_page):
    app.project_resource.icm.add_contributor()
    app.driver.implicitly_wait(10)
    assert app.project_resource.is_project_management_page()
    assert app.project_resource.icm.is_add_contributor_ui_elements()


@pytest.mark.regression_qf
@pytest.mark.qf_ui_smoke
@pytest.mark.dependency()
def test_add_single_contributor(app, qf_login, qf_refresh_page):
    app.project_resource.icm.add_single_contributor(icm_email, icm_name)
    app.driver.implicitly_wait(10)
    assert app.project_resource.icm.is_search_functionality(icm_email, icm_name)


@pytest.mark.regression_qf
@pytest.mark.qf_ui_smoke
def test_cancel_add_contributor(app, qf_login, qf_refresh_page):
    icm_email1, icm_name1 = faker.email(), faker.name()
    app.project_resource.icm.cancel_add_contributor(icm_email1, icm_name1)
    app.driver.implicitly_wait(10)
    try:
        app.project_resource.icm.find_contributor(icm_email1)
    except NoSuchElementException:
        assert True, "Cancel button works fine"


@pytest.mark.regression_qf
@pytest.mark.qf_ui_smoke
@pytest.mark.dependency(depends=["test_add_single_contributor"])
def test_search_functionality(app, qf_login, qf_refresh_page):
    app.driver.implicitly_wait(10)
    assert app.project_resource.icm.is_search_functionality(icm_email, icm_name)


@pytest.mark.regression_qf
@pytest.mark.dependency(depends=["test_search_functionality"])
@pytest.mark.parametrize("email, name", [(icm_email[5], icm_name[4]),
                                         (icm_email[2:5], icm_name[5:]),
                                         (icm_email[2:6], icm_name[4:7])])
def test_search_partial_functionality(app, qf_login, email, name, qf_refresh_page):
    app.project_resource.navigate_to_project_resource()
    app.driver.implicitly_wait(10)
    print(email, name)
    assert app.project_resource.icm.is_search_functionality(email, name, partial=True)


@pytest.mark.regression_qf
@pytest.mark.dependency(depends=["test_add_single_contributor"])
def test_add_existing_contributor(app, qf_login, qf_refresh_page):
    app.project_resource.icm.add_single_contributor(icm_email, icm_name)
    app.driver.implicitly_wait(10)
    assert app.verification.text_present_on_page("[3002:Entity Exists]Email already exists")


@pytest.mark.regression_qf
def test_add_contributor_with_invalid_email(app, qf_login, qf_refresh_page):
    app.project_resource.icm.click_add_contributors_button()
    app.project_resource.icm.enter_email('invalid_email')
    app.project_resource.icm.enter_name(icm_name)
    app.driver.implicitly_wait(5)
    assert app.verification.text_present_on_page("Please enter a valid email")


@pytest.mark.regression_qf
@pytest.mark.dependency()
def test_add_contributor_with_existing_name(app, qf_login, qf_refresh_page):
    new_email = faker.email()
    app.project_resource.icm.add_single_contributor(new_email, icm_name)
    app.driver.implicitly_wait(10)
    assert app.project_resource.icm.is_search_functionality(new_email, icm_name)


@pytest.mark.regression_qf
@pytest.mark.dependency(depends=["test_add_contributor_with_existing_name"])
def test_add_contributor_with_existing_email(app, qf_login, qf_refresh_page):
    new_name = faker.name()
    app.project_resource.icm.click_add_contributors_button()
    app.project_resource.icm.enter_email(icm_email)
    app.project_resource.icm.enter_name(new_name)
    app.project_resource.icm.click_add_button()
    app.driver.implicitly_wait(5)
    assert app.verification.text_present_on_page("[3002:Entity Exists]Email already exists")


@pytest.mark.regression_qf
@pytest.mark.dependency()
def test_add_contributor_with_blank_email(app, qf_login, qf_refresh_page):
    app.project_resource.navigate_to_project_resource()
    app.project_resource.icm.click_add_contributors_button()
    app.project_resource.icm.enter_email('')
    app.project_resource.icm.enter_name(icm_name)
    app.driver.implicitly_wait(10)
    assert app.verification.text_present_on_page("Please enter Email")


@pytest.mark.regression_qf
@pytest.mark.dependency(depends=["test_add_contributor_with_blank_email"])
def test_add_contributor_with_blank_email_and_name(app, qf_login, qf_refresh_page):
    app.project_resource.navigate_to_project_resource()
    app.project_resource.icm.click_add_contributors_button()
    app.project_resource.icm.enter_email('')
    app.project_resource.icm.enter_name('')
    app.driver.implicitly_wait(10)
    assert app.verification.text_present_on_page("Please enter Email")


@pytest.mark.regression_qf
@pytest.mark.dependency(depends=["test_add_contributor_with_blank_email_and_name"])
def test_add_contributor_with_invalid_name(app, qf_login, qf_refresh_page):
    app.project_resource.navigate_to_project_resource()
    app.project_resource.icm.click_add_contributors_button()
    app.project_resource.icm.enter_email(faker.email())
    app.project_resource.icm.enter_name('12345!@#$%^&*()_+')
    app.project_resource.icm.click_add_button()
    app.driver.implicitly_wait(10)
    assert app.verification.text_present_on_page("name: Name can only contain letters, numbers, and spaces; ")


@pytest.mark.regression_qf
def test_add_contributor_upper_case_email(app, qf_login, qf_refresh_page):
    email = faker.email().upper()
    app.project_resource.navigate_to_project_resource()
    app.project_resource.icm.click_add_contributors_button()
    app.project_resource.icm.enter_email(email)
    app.project_resource.icm.enter_name(icm_name)
    app.project_resource.icm.click_add_button()
    app.driver.implicitly_wait(10)
    assert app.project_resource.icm.is_search_functionality(email, icm_name)
