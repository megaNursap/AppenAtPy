import time

import allure
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait as Waiter
from selenium.webdriver.support import expected_conditions as ec
from adap.ui_automation.utils.js_utils import scroll_to_page_bottom

from adap.perf_platform.utils.logging import get_logger
from adap.ui_automation.utils.selenium_utils import find_element, find_elements, get_text_by_xpath, \
    click_element_by_xpath, is_element, send_keys_by_xpath, get_attribute_by_xpath

log = get_logger(__name__)


class UserScreeningPage:
    def __init__(self, app):
        self.app = app
        self.driver = self.app.driver

    _IFRAME_LOCATOR = "//div[@id='profile-builder-iframe-container']/iframe"
    _USER_SCREENING_LOCATOR = "//div[contains(text(), 'User screening')]"
    _PROJECT_QUALIFICATION_LOCATOR = "//div[contains(text(), 'Project qualification')]"
    _VIEW_NUMBERS_LOCATOR = "//button[contains(text(), 'View Numbers')]"
    _VIEW_NUMBERS_MODAL_LOCATOR = "//div[text()='Screening Numbers']/.."
    _SEARCH_USERS_LOCATOR = "//input[@placeholder='Search Users']"
    _FILTER_BY_STATUS_LOCATOR = f"{_SEARCH_USERS_LOCATOR}/../../following-sibling::div"
    _FILTERS_LOCATOR = "//img[contains(text(), ' Filters')]"
    _BULK_UPDATE_LOCATOR = "//button[contains(text(), 'Bulk Update')]"
    _BULK_UPDATE_OPTION_LOCATOR = "//div[contains(text(),'%s')]"
    _SELECT_REASON_DROPDOWN_LOCATOR = "//div[contains(text(), 'SELECT REASON')]/..//span[contains(text(), 'Select')]"
    _FIND_ROW_BY_ID_LOCATOR = "//span[contains(text(), '{}')]/../.."
    _FIND_ROW_BY_USERNAME_LOCATOR = "//a[contains(text(), '{}')]/../.."
    _FIND_ROW_BY_LAST_UPDATE_LOCATOR = "//span[contains(text(), '{}')]/../.."
    _ALL_USER_ROWS_LOCATOR = "//div[contains(text(), 'IP CHECK')]/../../../../tbody/tr"
    _TOTAL_USERS_AMOUNT_FOOTER_LOCATOR = ".//div[contains(text(), 'Showing')]"

    @allure.step('Check User screening iframe is opened and visible')
    def open(self):
        Waiter(self.driver, 10) \
            .until(
            ec.frame_to_be_available_and_switch_to_it((By.XPATH, self._IFRAME_LOCATOR)),
            f'User screening iframe can not be found ${self._IFRAME_LOCATOR}'
        )

        return self

    @allure.step('Get user row information')
    def get_user_row(
            self,
            u_id=None,
            username=None,
            last_update=None):
        if not locals().values():
            raise ValueError('None arguments provided')

        user_row_locator = \
            self._FIND_ROW_BY_ID_LOCATOR.format(u_id) if u_id else \
                self._FIND_ROW_BY_USERNAME_LOCATOR.format(username) if username else \
                    self._FIND_ROW_BY_LAST_UPDATE_LOCATOR.format(last_update)

        user_row_el = \
            find_element(self.driver, user_row_locator)

        return UserRowComponent(self.driver, user_row_el)

    @allure.step('Select user screening tab')
    def select_user_screening_tab(self):
        click_element_by_xpath(self.driver, self._USER_SCREENING_LOCATOR)

        return self

    @allure.step('Select project qualification tab')
    def select_project_qualification_tab(self):
        click_element_by_xpath(self.driver, self._PROJECT_QUALIFICATION_LOCATOR)

        return self

    @allure.step('Get all user rows')
    def get_all_user_rows(self):
        rows = find_elements(self.driver, self._ALL_USER_ROWS_LOCATOR)

        return [UserRowComponent(self.driver, row) for row in rows]

    @allure.step('Get first user row')
    def get_first_user_row(self):
        row = find_elements(self.driver, self._ALL_USER_ROWS_LOCATOR)[0]

        return UserRowComponent(self.driver, row)

    @allure.step('Filter users by status')
    def filter_status_by(self, status):
        supported_statuses = ['blocked', 'revoked', 'partner', 'express', 'registered', 'internal user',
                              'express to be converted', 'express active', 'express qualifying',
                              'payoneer setup', 'reactivation requested', 'on hold', 'expired contract',
                              'terminated', 'suspended', 'abandoned', 'rejected', 'active',
                              'in activation queue', 'contract pending', 'archived',
                              'staged', 'screened', 'application received', 'all statuses']
        if status.lower() not in supported_statuses:
            raise ValueError(f'Status is not supported, supported are: {supported_statuses}')

        # el = find_element(self.driver, self._FILTER_BY_STATUS_LOCATOR)
        el = find_element(self.driver, "//button[contains(text(),'View Numbers')]/../..//div[contains(@class,'container')]")
        el.click()
        click_element_by_xpath(el, f'.//*[contains(text(), "{status}")]')

        return self.wait_no_loading()

    @allure.step('Get current filter status')
    def get_current_filter_status(self):
        return get_text_by_xpath(self.driver, self._FILTER_BY_STATUS_LOCATOR)

    @allure.step('Reset filter status')
    def reset_filter_status(self):
        return self.filter_status_by('All Statuses')

    @allure.step('Search users')
    def search_users(self, text):
        send_keys_by_xpath(self.driver, self._SEARCH_USERS_LOCATOR, text)

        return self.wait_no_loading()

    @allure.step('Empty search users field')
    def empty_search_users_field(self):
        send_keys_by_xpath(self.driver, self._SEARCH_USERS_LOCATOR, (Keys.SHIFT, Keys.ARROW_UP, Keys.DELETE))

        return self.wait_no_loading()

    @allure.step('View Numbers')
    def view_numbers(self):
        click_element_by_xpath(self.driver, self._VIEW_NUMBERS_LOCATOR)
        self.app.verification.texts_present_on_page([
            'Screening Numbers',
            'Users Waiting To Be Screened',
            'Users Staged',
            'Users Requiring Activation'
        ])
        time.sleep(1)
        return ScreeningNumbersModalComponent(
            self, find_element(self.driver, self._VIEW_NUMBERS_MODAL_LOCATOR))

    @allure.step('Get total users amount footer text')
    def get_total_users_amount_footer_text(self):
        return get_text_by_xpath(self.driver, self._TOTAL_USERS_AMOUNT_FOOTER_LOCATOR)

    @allure.step('Get total users amount footer')
    def get_total_users_amount_footer(self):
        amount_str = self.get_total_users_amount_footer_text().split('of ')[1]
        return int(amount_str) if amount_str.isdigit() else 0

    @allure.step('Wait till there is no loading spinner')
    def wait_no_loading(self):
        self.app.verification.text_present_on_page('LOADING...', False)

        return self

    @allure.step('Click on Bulk Update button')
    def click_on_bulk_update_button(self):
        click_element_by_xpath(self.driver, self._BULK_UPDATE_LOCATOR)

        return self


    def choose_bulk_update_option(self, select_option, do_cancel=False):
        with allure.step(f"On Bulk Update select option {select_option}"):
            click_element_by_xpath(self.driver, self._BULK_UPDATE_OPTION_LOCATOR % select_option)
            self.app.verification.text_present_on_page(f'Bulk {select_option}')

            if do_cancel:
                self.app.navigation.click_btn('Cancel')
                self.app.verification.text_present_on_page('Bulk Update')

            return self


    def on_bulk_reject_select(self, reason, do_cancel=False):
        with allure.step(f"On Bulk Update select reject reason to {reason}"):
            click_element_by_xpath(self.driver, self._SELECT_REASON_DROPDOWN_LOCATOR)
            click_element_by_xpath(self.driver, f'//*[contains(text(), "{reason}")]')

            if do_cancel:
                self.app.navigation.click_btn('Cancel')

            return self


    def check_users_status(self, user_ids_lst, expected_status):
        with allure.step(f'Check list of users have status: {expected_status}'):
            for user_id in user_ids_lst:
                self.reset_filter_status().empty_search_users_field()
                self.search_users(user_id)

                user_row = self.get_first_user_row()
                user_current_status = user_row.status
                assert user_current_status == expected_status, f'User {user_id} has status {user_current_status}, expected: {expected_status}'


    @allure.step('Logout the user')
    def logout(self):
        self.app.driver.switch_to.parent_frame()
        self.app.ac_user.sign_out()

        return self

    def set_bulk_reject_reason(self, reason, do_cancel=False):
        with allure.step(f"On Bulk Update select reject reason to {reason}"):
            click_element_by_xpath(self.driver, self._SELECT_REASON_DROPDOWN_LOCATOR)
            click_element_by_xpath(self.driver, f'//*[contains(text(), "{reason}")]')

            if do_cancel:
                self.app.navigation.click_btn('Cancel')

            return self


    def define_operational_modal_window(self, action, row=None):
        return ScreeningActionModalWinComponent(self.driver, row, action)

class UserRowComponent:
    def __init__(self, driver, node):
        self.driver = driver
        self.node = node
        self.user_duplicate_signals = {}

    _CHECK_LOCATOR = "./td[position()=1]//span"
    _EXPAND_IMG_LOCATOR = "./td[position()=2]/span/span"
    _ID_LOCATOR = "./td[position()=3]/span"
    _NAME_LOCATOR = "./td[position()=4]//a"
    _STATUS_LOCATOR = "./td[position()=5]//span"
    _LAST_UPDATE_LOCATOR = "./td[position()=6]/span"
    _PROFILE_INFO_LOCATOR = "./td[position()=4]/div/div"
    _IP_CHECK_STATUS_TEXT_LOCATOR = "./td[position()=5]/div/div/div/span"
    _IP_CHECK_STATUS_LOCATOR = "./td[position()=5]/div/div/div/div[position()=1]"
    _IP_CHECK_STATUS_BUTTON_LOCATOR = "./td[position()=5]/div/div/div/div[last()]"
    _REVIEW_IP_CHECK_MODAL_LOCATOR = "//label[contains(text(), 'Detected IP')]/../../../../.."
    _MALICIOUSNESS_STATUS_LOCATOR = "./td[position()=6]/div/div/div"
    _MALICIOUSNESS_TEXT_LOCATOR = "./td[position()=6]/div/div/span"
    _MALICIOUSNESS_REVIEW_BUTTON_LOCATOR = "./td[position()=6]/div/div/div[last()]"
    _REVIEW_MALICIOUSNESS_MODAL_LOCATOR = "//h2[contains(text(), 'Fraud Check')]/../.."
    _DUPLICATES_CHECK_STATUS_TEXT_LOCATOR = "./td[position()=7]//label[contains(text(), 'Duplicates')]/../span"
    _DUPLICATES_CHECK_REVIEW_BUTTON_LOCATOR = \
        "./td[position()=7]//label[contains(text(), 'Duplicates')]/../div[last()]"
    _DUPLICATES_MODAL_LOCATOR = "//h2[contains(text(), 'Potential Duplicates')]/../.."
    _SUSPEND_BUTTON_LOCATOR = "//button[contains(text(), 'Suspend')]"
    _REINSTATE_BUTTON_LOCATOR = "//button[contains(text(), 'Reinstate')]"
    _PROCEED_BUTTON_LOCATOR = "//button[contains(text(), 'Proceed')]"
    _CHANGE_STATUS_SUCCESSFULLY_MSG_LOCATOR = "//span[contains(text(), '{}')]"
    _RESTART_QUALIFICATION_PROCESS_BUTTON_LOCATOR = "//button[contains(text(), 'Restart Qualification Process')]"
    _ACTION_BUTTON_LOCATOR = "//button[contains(text(), '{}')]"
    _MASTER_SERVICE_AGREEMENT_LINK_LOCATOR = "//a[contains(text(), 'View Master Services Agreement')]"
    _SELECT_REASON_DROPDOWN_LOCATOR = "//div[contains(text(), 'SELECT REASON')]/..//span[contains(text(), 'Select')]"
    _SELECT_COMPLETE_REASON_DROPDOWN_LOCATOR = "//h2[contains(text(), 'Complete')]/../..//span[contains(text(), 'Select')]"
    _DUPLICATES_SIGNAL_LST_LOCATOR = "//*[contains(text(),'Duplicate Signal:')]/.././/span"

    @allure.step('Get single user duplicates signals list')
    def get_single_user_duplicate_signals(self, min_num_of_signals=2):
        num_of_malicious = self.get_maliciousness_signals_count()
        if num_of_malicious >= min_num_of_signals:
            self.user_duplicate_signals['Maliciousness score'] = num_of_malicious

        els = find_elements(self.node, self._DUPLICATES_SIGNAL_LST_LOCATOR)
        if len(els) > 0:
            for index in range(len(els)):
                current_txt = els[index].text
                data = current_txt.split(':')
                if len(data) == 2:
                    num = int("".join([c for c in data[1] if str.isdigit(c)]))
                    if num > min_num_of_signals:
                        self.user_duplicate_signals[data[0]] = num

        print(f"For user with id: {self.id} collected: {self.user_duplicate_signals}")
        return self.user_duplicate_signals


    @allure.step('Select user row')
    def select(self):
        return click_element_by_xpath(self.node, self._CHECK_LOCATOR)

    @property
    @allure.step('Get user id')
    def id(self):
        return get_text_by_xpath(self.node, self._ID_LOCATOR)

    @property
    @allure.step('Get username')
    def username(self):
        return get_text_by_xpath(self.node, self._NAME_LOCATOR)

    @property
    @allure.step('Get user status')
    def status(self):
        return get_text_by_xpath(self.node, self._STATUS_LOCATOR)

    @property
    @allure.step('Get last update')
    def last_update(self):
        return get_text_by_xpath(self.node, self._LAST_UPDATE_LOCATOR)

    @property
    @allure.step('Get vendor url')
    def vendor_url(self):
        return find_element(self.node, self._NAME_LOCATOR).get_attribute('href')

    @allure.step('Click expand an user')
    def click_on_toggle_user_row(self, collapse=False):
        click_element_by_xpath(self.node, self._EXPAND_IMG_LOCATOR)

        if not collapse:
            Waiter(self.node, 10) \
                .until(
                lambda driver: driver.find_element('xpath',self._IP_CHECK_STATUS_LOCATOR).text.strip() != '',
                f'can not open user row or find any msg inside {self._IP_CHECK_STATUS_LOCATOR} on the page')

        time.sleep(1)
        return self

    @allure.step('Get profile information')
    def get_profile_info(self):
        return get_text_by_xpath(self.node, self._PROFILE_INFO_LOCATOR)

    @allure.step('Get ip check text')
    def get_ip_check_text(self):
        return get_text_by_xpath(self.node, self._IP_CHECK_STATUS_TEXT_LOCATOR)

    def get_ip_check_status(self):
        return get_text_by_xpath(self.node, self._IP_CHECK_STATUS_LOCATOR)

    @allure.step('Click on ip check review button')
    def click_ip_check_review_button(self):
        click_element_by_xpath(self.node, self._IP_CHECK_STATUS_BUTTON_LOCATOR)
        modal_el = find_element(
            self.driver,
            self._REVIEW_IP_CHECK_MODAL_LOCATOR)

        return IpCheckModalComponent(self.driver, modal_el)

    @allure.step('Get maliciousness check text')
    def get_maliciousness_check_text(self):
        return get_text_by_xpath(self.node, self._MALICIOUSNESS_TEXT_LOCATOR)

    @allure.step('Get maliciousness signals count')
    def get_maliciousness_signals_count(self):
        return int(self.get_maliciousness_check_text().split(' ')[0])

    @allure.step('Get maliciousness check status')
    def get_maliciousness_check_status(self):
        return get_text_by_xpath(self.node, self._MALICIOUSNESS_STATUS_LOCATOR)

    @allure.step('Click on maliciousness review button')
    def click_maliciousness_review_button(self):
        click_element_by_xpath(self.node, self._MALICIOUSNESS_REVIEW_BUTTON_LOCATOR)
        modal_el = find_element(
            self.driver,
            self._REVIEW_MALICIOUSNESS_MODAL_LOCATOR)

        return MaliciousnessModalComponent(self.driver, modal_el)

    @allure.step('Get duplicates check text')
    def get_duplicates_check_text(self):
        return get_text_by_xpath(self.node, self._DUPLICATES_CHECK_STATUS_TEXT_LOCATOR)

    @allure.step('Get duplicates check amount')
    def get_duplicates_check_amount(self):
        amount_str = self.get_duplicates_check_text().split(' ')[0]
        return int(amount_str) if amount_str.isdigit() else amount_str

    @allure.step('Click on duplicates check review button')
    def click_duplicates_check_review_button(self):
        click_element_by_xpath(self.node, self._DUPLICATES_CHECK_REVIEW_BUTTON_LOCATOR)
        modal_el = find_element(self.driver, self._DUPLICATES_MODAL_LOCATOR)

        return DuplicatesCheckModalComponent(self.driver, modal_el)

    @allure.step('Suspend an user')
    def suspend(self):
        click_element_by_xpath(self.driver, self._SUSPEND_BUTTON_LOCATOR)

        return self

    @allure.step('Proceed an operation for an user')
    def proceed(self, msg="User status changed successfully"):
        click_element_by_xpath(self.driver, self._PROCEED_BUTTON_LOCATOR)

        Waiter(self.driver, 15) \
            .until(
            ec.visibility_of_element_located((By.XPATH, self._CHANGE_STATUS_SUCCESSFULLY_MSG_LOCATOR.format(msg))),
            'There is no message tooltip found "%s"' % msg
        )

        Waiter(self.driver, 15) \
            .until(
            ec.invisibility_of_element_located((By.XPATH, self._CHANGE_STATUS_SUCCESSFULLY_MSG_LOCATOR.format(msg))),
            '"%s" is still visible' % msg
        )

        return self

    @allure.step('Check suspend button is visible')
    def suspend_button_is_present(self):
        return is_element(self.driver, self._SUSPEND_BUTTON_LOCATOR)

    @allure.step('Check reinstate button is visible')
    def reinstate_button_is_present(self):
        return is_element(self.driver, self._REINSTATE_BUTTON_LOCATOR)

    @allure.step('Restart qualification process for an user')
    def restart_qualification_process(self):
        click_element_by_xpath(self.driver, self._RESTART_QUALIFICATION_PROCESS_BUTTON_LOCATOR)

        return self

    @allure.step('Check restart qualification process button is visible')
    def restart_qualification_process_button_is_present(self):
        return is_element(self.driver, self._RESTART_QUALIFICATION_PROCESS_BUTTON_LOCATOR)

    @allure.step('Click on {action_name} action button')
    def click_on_action_button(self, action_name):
        click_element_by_xpath(self.driver, self._ACTION_BUTTON_LOCATOR.format(action_name))

        return self

    @allure.step('Click on view master services agreement')
    def view_master_service_agreement(self):
        click_element_by_xpath(self.driver, self._MASTER_SERVICE_AGREEMENT_LINK_LOCATOR)

        return self

    @allure.step('Select "{reason}" reason')
    def select_reason(self, reason):
        click_element_by_xpath(self.driver, self._SELECT_REASON_DROPDOWN_LOCATOR)
        click_element_by_xpath(self.driver, f'//*[contains(text(), "{reason}")]')

        return self

    @allure.step('Select complete "{reason}" reason')
    def select_complete_reason(self, reason):
        click_element_by_xpath(self.driver, self._SELECT_COMPLETE_REASON_DROPDOWN_LOCATOR)
        click_element_by_xpath(self.driver, f'//*[contains(text(), "{reason}")]')
        click_element_by_xpath(self.driver, self._SELECT_COMPLETE_REASON_DROPDOWN_LOCATOR)

        return self


class IpCheckModalComponent:
    def __init__(self, driver, node):
        self.driver = driver
        self.node = node

    _DETECTED_IP_ADDRESS_LOCATOR = ".//h1"
    _DETECTED_IP_LOCATION_LOCATOR = ".//label[contains(text(), 'Detected IP Location')]/../span"
    _CLOSE_BUTTON_LOCATOR = ".//button[position()=1]"

    @allure.step('Get detected ip address')
    def get_detected_ip_address(self):
        return get_text_by_xpath(self.node, self._DETECTED_IP_ADDRESS_LOCATOR)

    @allure.step('Get detected ip location')
    def get_detected_ip_location(self):
        return get_text_by_xpath(self.node, self._DETECTED_IP_LOCATION_LOCATOR)

    @allure.step('Click on close button')
    def close(self):
        return click_element_by_xpath(self.node, self._CLOSE_BUTTON_LOCATOR)


class MaliciousnessModalComponent:
    def __init__(self, driver, node):
        self.driver = driver
        self.node = node

    _FRAUD_AMOUNT_LOCATOR = './/h1'
    _FRAUD_STATUS_TEXT_LOCATOR = './/h1/../div[position()=1]'
    _FRAUD_SIGNALS_LOCATOR = './/h1/../div[last()]//table/tbody/tr'
    _CLOSE_BUTTON_LOCATOR = './/button[position()=1]'

    @allure.step('Get signals amount')
    def get_signals_count(self):
        return int(self.get_signals_count_text().split(' ')[0])

    @allure.step('Get signals amount text')
    def get_signals_count_text(self):
        return get_text_by_xpath(self.node, self._FRAUD_AMOUNT_LOCATOR)

    @allure.step('Get status text')
    def get_status_text(self):
        return get_text_by_xpath(self.node, self._FRAUD_STATUS_TEXT_LOCATOR)

    @allure.step('Get signals list')
    def get_signals_list(self):
        result = []
        rows = find_elements(self.node, self._FRAUD_SIGNALS_LOCATOR)
        for row in rows:
            cell = find_elements(row, './td')
            result.append({
                'type': cell[0].text,
                'text': cell[1].text
            })

        return result

    @allure.step('Click on close button')
    def close(self):
        return click_element_by_xpath(self.node, self._CLOSE_BUTTON_LOCATOR)


class DuplicatesCheckModalComponent:
    def __init__(self, driver, node):
        self.driver = driver
        self.node = node

    _TOTAL_DUPLICATES_TEXT_LOCATOR = ".//h1"
    _TOTAL_DUPLICATES_TEXT_TABLE_FOOTER_LOCATOR = ".//div[contains(text(), 'Showing')]"
    _CLOSE_BUTTON_LOCATOR = ".//button[position()=1]"
    _FIRST_DUPLICATION_VERIFICATION_ROW_LOCATOR = ".//div[text()='Duplicates Verification']/..//tbody/tr"

    @allure.step('Get total duplicates text')
    def get_total_duplicates_text(self):
        return get_text_by_xpath(self.node, self._TOTAL_DUPLICATES_TEXT_LOCATOR)

    @allure.step('Get total duplicates amount')
    def get_total_duplicates_amount(self):
        amount_str = self.get_total_duplicates_text().split(' ')[0]
        return int(amount_str) if amount_str.isdigit() else 0

    @allure.step('Get total duplicates table footer text')
    def get_total_duplicates_table_footer_text(self):
        return get_text_by_xpath(self.node, self._TOTAL_DUPLICATES_TEXT_TABLE_FOOTER_LOCATOR)

    @allure.step('Get total duplicates table footer amount')
    def get_total_duplicates_table_footer_amount(self):
        amount_str = self.get_total_duplicates_table_footer_text().split(' ')[-2]
        return int(amount_str) if amount_str.isdigit() else 0

    @allure.step('Click on close button')
    def close(self):
        return click_element_by_xpath(self.node, self._CLOSE_BUTTON_LOCATOR)

    @allure.step('Get first duplication verification row')
    def get_first_duplication_verification_row(self):
        row = find_elements(self.driver, self._FIRST_DUPLICATION_VERIFICATION_ROW_LOCATOR)[0]

        return DuplicationVerificationUserRowComponent(self.driver, row)


class DuplicationVerificationUserRowComponent:
    def __init__(self, driver, node):
        self.driver = driver
        self.node = node

    _TOGGLE_USER_ROW_LOCATOR = ".//td[last()]//img"
    _IS_NOT_DUPLICATE_CHECKBOX_LOCATOR = ".//div[contains(text(), 'This user is not a duplicate')]"
    _SAVE_CHANGES_BUTTON_LOCATOR = ".//button[text()='Save Changes']"

    @allure.step('Click expand an user')
    def click_on_toggle_user_row(self):
        click_element_by_xpath(self.node, self._TOGGLE_USER_ROW_LOCATOR)

        return self

    @allure.step('Click on "This user is not a duplicate"')
    def click_on_this_user_is_not_duplicate(self):
        click_element_by_xpath(self.node, self._IS_NOT_DUPLICATE_CHECKBOX_LOCATOR)

        return self

    @allure.step('Save changes')
    def save_changes(self):
        click_element_by_xpath(self.node, self._SAVE_CHANGES_BUTTON_LOCATOR)

        return self


class ScreeningNumbersModalComponent:
    def __init__(self, parent, node):
        self.parent = parent
        self.driver = parent.driver
        self.node = node

    _FILTER_BY_LOCATOR = ".//label[contains(text(), '{}')]/../following-sibling::button"
    _FILTER_BY_AMOUNT_LOCATOR = ".//label[contains(text(), '{}')]/preceding-sibling::h1"
    _FILTER_BY_USERS_WAITING_TO_BE_SCREENED_LOCATOR = \
        ".//label[contains(text(), 'Users Waiting To Be Screened')]/../following-sibling::button"
    _USERS_WAITING_TO_BE_SCREENED_AMOUNT_LOCATOR = \
        ".//label[contains(text(), 'Users Waiting To Be Screened')]/preceding-sibling::h1"
    _FILTER_BY_USERS_STAGED_LOCATOR = ".//label[text()=='Users Staged']/../following-sibling::button"
    _USERS_STAGED_AMOUNT_LOCATOR = ".//label[text()=='Users Staged']/preceding-sibling::h1"
    _FILTER_BY_USERS_REQUIRING_ACTIVATION_LOCATOR \
        = ".//label[text()=='Users Requiring Activation']/../following-sibling::button"
    _USERS_REQUIRING_ACTIVATION_AMOUNT_LOCATOR \
        = ".//label[text()=='Users Requiring Activation']/preceding-sibling::h1"
    _CLOSE_BUTTON_LOCATOR = ".//button[text()=='Close']"

    @allure.step('Filter by "{filter_name}"')
    def filter_by(self, filter_name):
        click_element_by_xpath(self.driver, self._FILTER_BY_LOCATOR.format(filter_name))

        return self.parent.wait_no_loading()

    @allure.step('Get filter by "{filter_name}" amount')
    def get_filter_by_users_amount(self, filter_name):
        return get_text_by_xpath(self.node, self._FILTER_BY_AMOUNT_LOCATOR.format(filter_name))

    @allure.step('Filter by users waiting to be screened')
    def filter_by_users_waiting_to_be_screened(self):
        click_element_by_xpath(self.node, self._FILTER_BY_USERS_WAITING_TO_BE_SCREENED_LOCATOR)

        return self.parent.wait_no_loading()

    @allure.step('Get users waiting to be screened amount')
    def get_users_waiting_to_be_screened_amount(self):
        return get_text_by_xpath(self.node, self._USERS_WAITING_TO_BE_SCREENED_AMOUNT_LOCATOR)

    @allure.step('Filter by users staged')
    def filter_by_users_staged(self):
        click_element_by_xpath(self.node, self._FILTER_BY_USERS_STAGED_LOCATOR)

        return self.parent.wait_no_loading()

    @allure.step('Get users staged amount')
    def get_users_staged_amount(self):
        return get_text_by_xpath(self.node, self._USERS_STAGED_AMOUNT_LOCATOR)

    @allure.step('Filter by users requiring activation')
    def filter_by_users_requiring_activation(self):
        click_element_by_xpath(self.node, self._FILTER_BY_USERS_REQUIRING_ACTIVATION_LOCATOR)

        return self.parent.wait_no_loading()

    @allure.step('Get users requiring activation amount')
    def get_users_requiring_activation_amount(self):
        return get_text_by_xpath(self.node, self._USERS_REQUIRING_ACTIVATION_AMOUNT_LOCATOR)


class ScreeningActionModalWinComponent:

    _CONTAINER_LOCATOR = "//div[@role='dialog']"
    _BUTTON_CLOSE_LOCATOR = f"{_CONTAINER_LOCATOR}//button[./img[contains(text(),'Close modal')]]"

    _TITLE_LOCATOR = f"{_CONTAINER_LOCATOR}//h2"
    _WIN_CONFIRM_PROMPT_LOCATOR = "By clicking on ”Proceed” this user will be moved to the ”screened” user status."

    _BUTTON_LOCATOR = f"{_CONTAINER_LOCATOR}//button[contains(text(), '%s')]"

    _SELECT_REASON_DD_CONTAINER_LOCATOR = "//div[@role='dialog']//div[contains(@class,'-container')]"
    _SELECT_REASON_DROPDOWN_LOCATOR = "//div[contains(text(), 'SELECT REASON')]/..//div[.//span[contains(text(),'Select')]]"
    # _SELECT_REASON_OPTION_LOCATOR = "//input[@id='react-select-10-input']//div[contains(@class,'select-option')][.//div[text()='%s']]"
    _SELECT_REASON_OPTION_LOCATOR = "//div[contains(@id,'react-select-10-option-%s')]"

    _SELECT_FRAUD_DROPDOWN_LABEL_LOCATOR = "//div[contains(text(),'SELECT FRAUD IDENTIFIED')]"
    _SELECT_FRAUD_DROPDOWN_LOCATOR = f"{_SELECT_FRAUD_DROPDOWN_LABEL_LOCATOR}/..//span[contains(text(), 'Select')]"
    _SELECT_FRAUD_DROPDOWN_TOTALCOUNTER_LOCATOR = f"{_SELECT_FRAUD_DROPDOWN_LOCATOR}/../div[1]"
    _SELECT_FRAUD_OPTION_LOCATOR = "//div[contains(@id,'react-select-11-option')][.//*[contains(text(),'%s')]]"

    _SELECT_SIGNALS_DROPDOWN_LABEL_LOCATOR = "//div[contains(text(),'Which signals were not strong enough to indicate concern? (Select all that apply):')]"
    _SELECT_SIGNALS_DROPDOWN_LOCATOR = f"{_SELECT_SIGNALS_DROPDOWN_LABEL_LOCATOR}/..//div[contains(@class, 'control')]"
    _SELECT_SIGNALS_DROPDOWN_TOTALCOUNTER_LOCATOR = "//div[contains(text(),'Which signals were not strong enough to indicate concern? (Select all that apply):')]/..//div[contains(@class,'control')]/div[./span[contains(text(),'Select')]]/div[1]"
    _SELECT_SIGNALS_OPTION_LOCATOR = "//div[contains(@class,'select-option') and contains(@id,'react-select-10-option')][.//*[contains(text(),'%s')]]"

    _INTERNAL_NOTE_AREA_LOCATOR = "//div[contains(text(),'INTERNAL NOTE (OPTIONAL)'/.."

    _CHANGE_STATUS_SUCCESSFULLY_MSG_LOCATOR = "//span[contains(text(), 'User status changed successfully')]"
    known_reject_reasons_list = {'Did not meet project requirement': '0', 'Duplicate or fraud': '1',
                                'DNH state for US and country': '2', 'Other': '3'}
    known_frauds_list = ('High malicious score', 'Tumbling email', 'Large number of potential duplicates',
                  'Multiple matching attributes - Full name',
                  'Multiple matching attributes - Email', 'Multiple matching attributes - Phone',
                  'Multiple matching attributes - Address',
                  'Multiple matching attributes - Photo ID',
                  'Multiple matching attributes - IP Address')

    known_signals_list = ('Full name', 'Email', 'Phone', 'Address', 'Registration IP', 'User session IPs', 'Maliciousness score')


    def __init__(self, driver, action, node=None):

        self.driver = driver
        self.action = action
        if node:
            self.node = node


    @allure.step('Select reject "{reason}" reason')
    def select_reason(self, reason):
        scroll_to_page_bottom(self.driver)

        dd_container = find_elements(self.driver, self._SELECT_REASON_DROPDOWN_LOCATOR)
        assert len(dd_container) > 0, "Dropdown select not found"
        dd_container[0].click()

        new_xpath = None
        print("Reason: {reason}")

        for key, val in self.known_reject_reasons_list.items():
            print(f"KEY: {key}")
            if key.lower() == reason.lower():
                new_xpath = self._SELECT_REASON_OPTION_LOCATOR % val
                break

        click_element_by_xpath(self.driver, new_xpath)
        time.sleep(4)


    @allure.step('Select {num_of_frauds} frauds')
    def select_frauds(self, num_of_frauds):
        if num_of_frauds == 100:
            num_of_frauds = len(self.known_frauds_list)

        click_element_by_xpath(self.driver, self._SELECT_FRAUD_DROPDOWN_LOCATOR)

        selected = []
        for index, fraud in enumerate(self.known_frauds_list):
            if index < num_of_frauds:
                click_element_by_xpath(self.driver, self._SELECT_FRAUD_OPTION_LOCATOR % fraud)
                selected.append(fraud)

        click_element_by_xpath(self.driver, self._SELECT_FRAUD_DROPDOWN_LOCATOR)
        return num_of_frauds, selected


    @allure.step("Get content of total frauds counter")
    def get_content_of_total_frauds_counter(self):
        counter = get_text_by_xpath(self.driver, self._SELECT_FRAUD_DROPDOWN_TOTALCOUNTER_LOCATOR)
        return int(counter)


    @allure.step("Get content of total selected signals counter")
    def get_content_of_total_selected_signals_counter(self):
        counter = get_text_by_xpath(self.driver, self._SELECT_SIGNALS_DROPDOWN_TOTALCOUNTER_LOCATOR)
        return int(counter)

    def check_all_not_strong_signals_selected(self, signals_list):
        for signal in signals_list:
            el = find_elements(self.driver, "//div[contains(text(),'%s')]" % signal)
            assert len(el) > 0, f"Element {signal} not found"


    @allure.step("Select signals: {num_of_signals}")
    def select_signals(self, num_of_signals):
        signals_list = self.known_signals_list

        if num_of_signals == 100:
            num_of_signals = len(signals_list)

        scroll_to_page_bottom(self.driver)
        click_element_by_xpath(self.driver, self._SELECT_SIGNALS_DROPDOWN_LOCATOR)

        selected = []

        for index, signal in enumerate(signals_list):
            if index < num_of_signals:
                click_element_by_xpath(self.driver,
                                       self._SELECT_SIGNALS_OPTION_LOCATOR % signal)
                selected.append(signal)

        click_element_by_xpath(self.driver, self._SELECT_SIGNALS_DROPDOWN_LABEL_LOCATOR)
        return num_of_signals, selected


    @allure.step("Get current modal window title")
    def get_modal_win_title(self):
        return get_text_by_xpath(self.driver, self._TITLE_LOCATOR)


    @allure.step("Click on {btn_name} button")
    def manage_button(self, btn_name, proceed_timeout=5):
        click_element_by_xpath(self.driver, self._BUTTON_LOCATOR % btn_name)
        return self.wait_for_proceed_completed(timeout=proceed_timeout)


    @allure.step("Add internal note")
    def add_internal_note(self, note):
        send_keys_by_xpath(self.driver, self._INTERNAL_NOTE_AREA_LOCATOR, note)


    @allure.step("Get action modal window confirmation prompt")
    def get_action_modal_win_confirmation_prompt(self):
        return get_text_by_xpath(self.driver, self._WIN_CONFIRM_PROMPT_LOCATOR)

    def is_proceed_button_disabled(self):
        btn_name = 'Proceed'
        xpath = self._BUTTON_LOCATOR % btn_name
        els = find_elements(self.driver, xpath)
        assert len(els) > 0, f"Button '{btn_name}' not found"
        return get_attribute_by_xpath(self.driver, xpath, 'disabled')


    allure.step("Check is operation modal window open")
    def is_modal_win_open(self):
        els = find_elements(self.driver, self._BUTTON_CLOSE_LOCATOR)
        return len(els) > 0


    @allure.step("Close operation modal window if displayed")
    def close_dialog(self):
        els = find_elements(self.driver, self._BUTTON_CLOSE_LOCATOR)
        if len(els) > 0:
            els[0].click()


    @allure.step("Wait for operation proceed")
    def wait_for_proceed_completed(self, timeout = 5):
        counter = 0

        while counter <= timeout:
            if self.is_modal_win_open():
                time.sleep(1)
                counter += 1
            else:
                print(f"Operation modal window closed in {counter} secs")
                break

        return True if not self.is_modal_win_open() else False