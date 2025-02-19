import os
import re
import time
from telnetlib import EC

import allure
import pytest
import logging
from selenium import webdriver
from seleniumwire import webdriver as webdriver_wire
from selenium.common.exceptions import NoSuchElementException, WebDriverException, TimeoutException
from selenium.webdriver.support.wait import WebDriverWait

from adap.api_automation.utils.data_util import get_test_data
from adap.api_automation.utils.helpers import get_current_ip
from adap.settings import Config
from contextlib import contextmanager
from selenium.webdriver.common.by import By
from adap.perf_platform.utils.logging import get_logger
from selenium.webdriver import DesiredCapabilities, ActionChains, Keys
from selenium.webdriver.support import expected_conditions as ec

from adap.ui_automation.utils.js_utils import element_to_the_middle

LOGGER = get_logger(__name__)
logging.getLogger('hpack').setLevel(logging.ERROR)
logging.getLogger('urllib3.connectionpool').setLevel(logging.ERROR)
logging.getLogger('seleniumwire').setLevel(logging.ERROR)


def enable_download_in_headless_chrome(driver, download_dir):
    """
    there is currently a "feature" in chrome where
    headless does not allow file download: https://bugs.chromium.org/p/chromium/issues/detail?id=696481
    This method is a hacky work-around until the official chromewdriver support for this.
    Requires chrome version 62.0.3196.0 or above.
    """
    # add missing support for chrome "send_command"  to selenium webwdriver
    driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
    #
    params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': download_dir}}
    command_result = driver.execute("send_command", params)
    # print("\nresponse from browser:")
    # for key in command_result:
    #     print("result:" + key + ":" + str(command_result[key]))


def set_up_driver(tmp_file=None, driver_type='local', os_system=None, browser=None, request=None, session_id=None, ):
    if driver_type == 'local':
        print("local selenium")
        return set_up_local_selenium_chrome(tmp_file)
    elif driver_type == 'browser_stack':
        return set_up_browser_stack_selenium(tmp_file, request=request, session_id=session_id)


def set_up_browser_stack_selenium(tmp_file=None, os_system='Windows 10', browser='Chrome 85', request=None,
                                  session_id=None, localIdentifier=None):
    BROWSERSTACK_URL = 'https://tracyyu2:Muq8tTy3eXd3erRF3WRY@hub-cloud.browserstack.com/wd/hub'
    # BROWSERSTACK_URL = 'https://marinasenyutina1:XXtyPqvr7DewkDx4VRCA@hub-cloud.browserstack.com/wd/hub'

    print("SYSTEM", os_system)
    _os = os_system.split(' ')[0]
    _os_version = os_system.split(' ')[1]
    _browser = browser.split(' ')[0]
    _browser_version = browser.split(' ')[1]

    desired_cap = {
        'os': _os,
        'os_version': _os_version,
        'browser': _browser,
        'resolution': '1920x1200',
        'browser_version': _browser_version,
        'name': request.node.name,
        'project': pytest.env,
        'build': session_id,
        'browserstack.local': 'true'
    }

    driver = webdriver.Remote(command_executor=BROWSERSTACK_URL, desired_capabilities=desired_cap)
    driver.maximize_window()
    return driver


# Create a request interceptor
def interceptor_ac(request):
    del request.headers['Appen-Kasada-Postman-Bypass']  # Delete the header first
    bypass = get_test_data('selenium_param', 'bypass')
    request.headers['Appen-Kasada-Postman-Bypass'] = bypass


def set_up_local_selenium_chrome(tmp_file=None):
    print("===== set up  driver =====")
    LOGGER.debug(f"OS ENV driver: %s" % os.environ)
    LOGGER.info(f"Current IP: {get_current_ip()} ")

    # Check if the current version of chromedriver exists
    # and if it doesn't exist, download it automatically,
    # then add chromedriver to path
    # chromedriver_autoinstaller.install()

    chrome_profile = webdriver.ChromeOptions()

    profile_prefs = {'download.default_directory': str(tmp_file),
                     'download.prompt_for_download': False,
                     'download.directory_upgrade': True,
                     'safebrowsing.enabled': False,
                     'safebrowsing.disable_download_protection': True,
                     'unexpectedAlertBehaviour': True,
                     'credentials_enable_service': False,
                     'profile.password_manager_enabled': False,
                     }

    chrome_profile.add_experimental_option("prefs", profile_prefs)
    chrome_profile.add_experimental_option("detach", True)

    chrome_capabilities = DesiredCapabilities.CHROME
    chrome_capabilities['loggingPrefs'] = {'browser': 'ALL'}

    if os.environ.get('DISPLAY'):
        chrome_profile.add_argument('--headless=new')
    # chrome_profile.add_argument('--headless')
    chrome_profile.add_argument('--dns-prefetch-disable')
    chrome_profile.add_argument("--password-store=basic")
    chrome_profile.add_argument('--no-sandbox')
    # chrome_profile.add_argument('--incognito')
    chrome_profile.add_argument('--disable-gpu')
    chrome_profile.add_argument('--window-size=1600,1200')
    chrome_profile.add_argument('--no-cache')
    chrome_profile.add_argument('--disable-dev-shm-usage')
    chrome_profile.add_argument('--ignore-ssl-errors=yes')
    chrome_profile.add_argument('--ignore-certificate-errors')
    chrome_profile.add_argument('--disable-arguments')
    chrome_profile.add_argument('--disable-site-isolation-trials')
    # chrome_profile.setAlertBehavior(UserPromptHandler.ACCEPT)

    # chrome_profile.add_argument('--auto-open-devtools-for-tabs')
    chrome_profile.add_experimental_option("excludeSwitches", ['enable-automation'])

    """"
    ENV:
        for AC: stage - ac_stage; qa - ac_qa; ac_integration;
        adap_ac - for integration tests,
        gap - gap
        adap production - live
    """
    if not os.environ.get('DISPLAY'):
        options = {
            'exclude_hosts': ['client.integration.cf3.us', 'annotate.integration.cf3.us']
        }
        chrome_capabilities['acceptInsecureCerts'] = True
        driver = webdriver_wire.Chrome(chrome_options=chrome_profile, desired_capabilities=chrome_capabilities,
                                       seleniumwire_options=options)
        driver.request_interceptor = interceptor_ac
    else:
        driver = webdriver.Chrome(chrome_options=chrome_profile, desired_capabilities=chrome_capabilities)

    if os.environ.get('DISPLAY'):
        enable_download_in_headless_chrome(driver, str(tmp_file))

    driver.implicitly_wait(7)

    return driver


def mobile_evaluation(driver):
    set_device_metrics_override = dict({
        "width": 375,
        "height": 812,
        "deviceScaleFactor": 50,
        "mobile": True
    })
    driver.execute_cdp_cmd("Emulation.setDeviceMetricsOverride", set_device_metrics_override)


def find_element(driver_or_element, value, mode=By.XPATH):
    return driver_or_element.find_element(mode, value)


def find_element_by_css_selector(driver_or_element, value, mode=By.CSS_SELECTOR):
    return driver_or_element.find_element(mode, value)


def find_elements(driver_or_element, value, mode=By.XPATH):
    return driver_or_element.find_elements(mode, value)


def find_elements_by_css_selector(driver_or_element, value, mode=By.CSS_SELECTOR):
    return driver_or_element.find_elements(mode, value)


def go_to_page(driver, value, mobile_device=False):
    if mobile_device:
        mobile_evaluation(driver)

    driver.get(value)
    time.sleep(2)


def create_screenshot(driver, name=None):
    try:
        filename = f"{name} {time.strftime('%d-%m-%Y %I-%M-%S %p')}.png"
        path = os.path.abspath(Config.APP_DIR + "/Failed_scenarios")
        if not os.path.exists(path):
            os.makedirs(path)
        fullpath = os.path.join(path, filename)
        allure.attach(driver.get_screenshot_as_png())
        driver.save_screenshot(fullpath)
        assert driver.save_screenshot(fullpath), "Failed to take screenshot"
        LOGGER.info(f"Screenshot saved to {fullpath}")
        return fullpath
    except:
        return ""


def create_screenshot_for_element(driver, el, full_name):
    element_to_the_middle(driver, el, center=True)
    time.sleep(2)
    el.screenshot(str(full_name))
    return full_name


def get_text_by_xpath(driver, xpath):
    el = find_elements(driver, value=xpath)
    if len(el) > 0:
        return el[0].text
    else:
        return ''


def get_text_by_css_selector(driver, css_selector):
    el = find_elements_by_css_selector(driver, value=css_selector)
    if len(el) > 0:
        return el[0].text
    else:
        return ''


def click_element_by_xpath(driver, xpath, msg=None, timeout=0, index=0):
    el = find_elements(driver, xpath)
    assert len(el) > 0, "Element has not been found by xpath: %s" % xpath if not msg else msg
    el[index].click()
    time.sleep(timeout)


def click_element(driver, locator):
    try:
        if locator.startswith("//"):
            element = driver.find_element(By.XPATH, locator)
        else:
            element = driver.find_element(By.CSS_SELECTOR, locator)
        element.click()
    except NoSuchElementException:
        print(f"Element not found: {locator}")


def send_keys_to_element(driver, locator, text, clear_current=False, mode='selenium'):
    try:
        if locator.startswith("//"):
            element = driver.find_element(By.XPATH, locator)
        else:
            element = driver.find_element(By.CSS_SELECTOR, locator)
        if clear_current:
            if mode == 'selenium':
                element.clear()
                time.sleep(4)
            elif mode == 'keys':
                for i in range(len(text)):
                    element.send_keys(Keys.BACK_SPACE)
        element.send_keys(text)
    except NoSuchElementException:
        print(f"Element not found: {locator}")


def click_element_by_text(driver, text):
    el = find_element(driver, "//*[text()='%s']" % text)
    el.click()


def click_element_by_css_selector(driver, css_selector, msg=None, timeout=0, index=0):
    el = find_elements_by_css_selector(driver, css_selector)
    assert len(el) > 0, "Element has not been found by css_selector: %s" % css_selector if not msg else msg
    el[index].click()
    time.sleep(timeout)


def double_click_element_by_xpath(driver, xpath):
    el = find_elements(driver, xpath)
    assert len(el) > 0, "Element has not been found by xpath: %s" % xpath
    action = ActionChains(driver)
    action.double_click(el[0]).perform()


def double_click_on_element(driver, element):
    action = ActionChains(driver)
    action.double_click(element).perform()


def send_keys_by_xpath(driver, xpath, value, clear_current=False, mode='selenium'):
    el = find_elements(driver, xpath)
    assert len(el) > 0, "Element has not been found by xpath: %s" % xpath
    if clear_current:
        if mode == 'selenium':
            el[0].clear()
            time.sleep(4)
        elif mode == 'keys':
            for i in range(len(value)):
                el[0].send_keys(Keys.BACK_SPACE)

    el[0].send_keys(value)


def send_keys_by_css_selector(driver, css_selector, value, clear_current=False, mode='selenium'):
    el = find_elements_by_css_selector(driver, css_selector)
    assert len(el) > 0, "Element has not been found by css selector: %s" % css_selector
    if clear_current:
        if mode == 'selenium':
            el[0].clear()
            time.sleep(4)
        elif mode == 'keys':
            for i in range(len(value)):
                el[0].send_keys(Keys.BACK_SPACE)

    el[0].send_keys(value)


def click_and_send_keys_by_xpath(driver, xpath, value, clear_current=False):
    click_element_by_xpath(driver, xpath)
    send_keys_by_xpath(driver, xpath, value, clear_current)


def click_and_send_keys_by_css_selector(driver, css_selector, value, clear_current=False):
    click_element_by_css_selector(driver, css_selector)
    send_keys_by_css_selector(driver, css_selector, value, clear_current)


def set_value_by_css_selector(driver, css_selector, value):
    # Locate the element
    element = find_element_by_css_selector(driver, css_selector)
    # Clear the field using JavaScript
    driver.execute_script("arguments[0].value = '';", element)
    # Set the value using JavaScript
    driver.execute_script(f"arguments[0].value = '{value}';", element)
    driver.execute_script("arguments[0].dispatchEvent(new Event('input'));", element)


def get_attribute_by_xpath(driver, xpath, attribute_name):
    el = find_elements(driver, xpath)
    assert len(el) > 0, "Element has not been found by xpath: %s" % xpath
    return el[0].get_attribute(attribute_name)


def clear_text_field_by_xpath(driver, xpath):
    el = find_elements(driver, xpath)
    assert len(el) > 0, "Element has not been found by xpath: %s" % xpath


def move_to_element_with_offset(driver, el, X, Y):
    ac = ActionChains(driver)
    ac.move_to_element_with_offset(el, X, Y).pause(2).click().perform()


def nav_timing(driver):
    ''' Use Navigation Timing  API to calculate the timings that matter the most '''
    navigationStart = driver.execute_script("return window.performance.timing.navigationStart")
    responseStart = driver.execute_script("return window.performance.timing.responseStart")
    domComplete = driver.execute_script("return window.performance.timing.domComplete")
    ''' Calculate the performance'''
    backendPerformance_calc = responseStart - navigationStart
    frontendPerformance_calc = domComplete - responseStart
    LOGGER.info({
        'page_title': driver.title,
        'page_url': driver.current_url,
        'backend_performance': backendPerformance_calc,
        'frontend_performance': frontendPerformance_calc})


def send_keys_and_select_by_xpath(driver, xpath, value, clear_current=False):
    el = find_elements(driver, xpath)
    assert el, "Element has not been found by xpath: %s" % xpath
    if clear_current:
        el[0].clear()
    el[0].send_keys(value)
    el[0].send_keys(Keys.ENTER)
    time.sleep(1)


@contextmanager
def iframe_context(app, iframe):
    """
    Context to enter and exit iframe
    params:
        app (Application): instance of adap.ui_automation.services_config.application.Application
        iframe (WebElement): iframe to work inside of
    """
    LOGGER.debug(f'switching to {iframe}')
    app.navigation.switch_to_frame(iframe)
    yield
    LOGGER.debug('switching to default content')
    app.driver.switch_to.parent_frame()


def is_element(driver, xpath):
    try:
        find_element(driver, xpath)
        return True
    except NoSuchElementException:
        return False


def is_element_visible_by_css_selector(driver, css_selector):
    try:
        find_element_by_css_selector(driver, css_selector)
        return True
    except NoSuchElementException:
        return False


def click_by_action(driver, element, class_name):
    ac = ActionChains(driver)
    el = WebDriverWait(driver, 20).until(
        ec.visibility_of_element_located((By.CLASS_NAME, class_name)))
    ac.move_to_element(el).click(element) \
        .perform()


def move_to_element(driver, element):
    ActionChains(driver).scroll_to_element(element).pause(2).click(element).perform()


def scroll_to_element_by_action(driver, element):
    ActionChains(driver).scroll_to_element(element).pause(4).perform()


def split_text(text, return_part=1):
    specific_data = text.split("\n")
    return specific_data[return_part]


def modify_text(text, regex):
    new_text = re.findall(regex, text)
    new_text[1] = "_" + new_text[1].lower()
    return ''.join(new_text)


def is_text_present(driver, text):
    """
    Verifies if the specified text is present on the current page.

    :param driver: The Selenium WebDriver instance.
    :param text: The text to search for on the page.
    :return: True if the text is found, False otherwise.
    """
    return text in driver.page_source


def get_console_log(driver, method_name='default'):
    LOGGER.info({
        'test_name': f"{method_name}",
        'console_log': driver.get_log('browser')})


def input_list_contains_output_list(list_input, list_output, modify_list=False, value_modify="customer_id_for_"):
    if modify_list:
        new_list = [f'{value_modify}{e}' for e in list_output]
        return any(item.lower() in list_input for item in new_list)
    else:
        return all(item.lower() in list_input for item in list_output)


def delete_by_action(driver, element):
    ActionChains(driver).click(element).send_keys(Keys.DELETE).perform()


def select_option_value(driver, select_name, value):
    driver.find_element('xpath',
                        f"//select[@name='{select_name}']//option[text()='{value}']").click()
    time.sleep(2)


def clear_field_by_attribute_value(driver, element):
    driver.execute_script("arguments[0].value = ''", element)
    time.sleep(2)


def set_field_by_attribute_value(driver, element, value):
    driver.execute_script(f"arguments[0].value = '{value}'", element)
    time.sleep(2)


def click_by_java_script(driver, element):
    driver.execute_script("arguments[0].click();", element)
    time.sleep(2)


def click_and_send_keys_by_js(driver, xpath, value, clear_current=False):
    click_by_java_script(driver, find_element(driver, xpath))
    send_keys_by_xpath(driver, xpath, value, clear_current)


def sleep_for_seconds(seconds):
    """
    Sleep for the specified number of seconds.

    :param seconds: Number of seconds to sleep
    """
    time.sleep(seconds)
