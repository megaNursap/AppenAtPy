from adap.e2e_automation.services_config.job_api_support import create_job_from_config_api
from adap.ui_automation.utils.page_element_utils import click_rebrand_popover
from adap.api_automation.utils.data_util import get_user
from adap.ui_automation.utils import js_utils
from adap.ui_automation.lidar.support.image_diff import compare_images
from adap.ui_automation.utils import selenium_utils
from adap.perf_platform.utils.logging import get_logger
from adap.settings import Config
import random
import pytest
import allure
import os

log = get_logger(__name__)

# baseline screenshots are for 'sailing-boats-407841_1280.jpg'
_base_dir = f"{Config.APP_DIR}/data/sda/baseline_screenshots/"
baseline_screenshots = {
    'img': f"{_base_dir}/unit_view_img_tag.png",
    'shapes': f"{_base_dir}/unit_view_shapes_tag.png",
    'img-alone': f"{_base_dir}/unit_view_img-alone_tag.png"
}


def create_sda_job(user, job_cml_filepath, units_filepath):

    with open(job_cml_filepath, 'r') as f:
            job_cml =  f.read()
    
    config = {
        "job": {
            "title": "QA Test - SDA",
            "instructions": "<h1>Overview</h1>",
            "cml": job_cml,
            "units_per_assignment": 1,
            "gold_per_assignment": 0,
            "judgments_per_unit": 1,
            "project_number": "PN000112"
        },
        "data_upload": [units_filepath],
        "launch": True,
        "rows_to_launch": 10,
        "external_crowd": False,
        "channels": Config.CHANNELS,  # default; vcare, listia
        "level": Config.CROWD_LEVEL,  # default: unleveled
        "ontology": [
            {'description': "", 'class_name': "Boat", 'display_color': "#FF1744", 'relationship_types': []},
            ],
        "user_email": user['email'],
        "user_password": user['password'],
        "jwt_token": user['jwt_token'],
        'auto_order': {
            'bypass_estimated_fund_limit': Config.BYPASS_ESTIMATED_FUND_LIMIT,
            'units_remain_finalized': Config.UNITS_REMAIN_FINALIZED,
            'schedule_fifo': True,
            'auto_order_timeout': Config.AUTO_ORDER_TIMEOUT
        }
    }

    job_id = create_job_from_config_api(config, Config.ENV, user['api_key'])
    return job_id

def create_sda_s3_job():
    """
    Create and launch an SDA job using API.
    Units data is hosted on AWS S3 bucket.
    """
    user = get_user('test_sda', env=Config.ENV)
    units_csv = f"{Config.APP_DIR}/data/sda/units.csv"
    job_cml_filepath = f"{Config.APP_DIR}/data/sda/job_cml.txt"
    return create_sda_job(user, job_cml_filepath, units_csv)

def create_sda_azure_job():
    """
    Create and launch an SDA job using API.
    Units data is hosted on Azure bucket.
    """
    user = get_user('test_sda', env=Config.ENV)
    units_csv = f"{Config.APP_DIR}/data/sda/units_azure.csv"
    job_cml_filepath = f"{Config.APP_DIR}/data/sda/job_cml_azure.txt"
    return create_sda_job(user, job_cml_filepath, units_csv)


def create_sda_gcp_job():
    """
    Create and launch an SDA job using API.
    Units data is hosted on GCP bucket.
    """
    user = get_user('test_sda', env=Config.ENV)
    units_csv = f"{Config.APP_DIR}/data/sda/units_gcp.csv"
    job_cml_filepath = f"{Config.APP_DIR}/data/sda/job_cml_gcp.txt"
    return create_sda_job(user, job_cml_filepath, units_csv)

class SDA:
    def __init__(self, app):
        self.app = app
        self.driver = self.app.driver
    
    def find_elements(self, xpath):
        return selenium_utils.find_elements(self.driver, xpath)
    
    def sign_in_as(self, team):
        with allure.step('Sign in for {team}'):
#             if team == 's3':
#                 user = get_user('test_sda', env=pytest.env)
#             elif team == 'azure':
#                 user = get_user('test_sda_azure', env=pytest.env)
#             else:
#                 raise Exception(f'User is unknown for team {team}')
            user = get_user('test_sda', env=pytest.env)
            if self.app.user.current_user == user['user_name']:
                log.debug(f"Already logged in as {user['user_name']}")
                return
            elif self.app.user.current_user is not None:
                self.driver.switch_to.parent_frame()
                self.app.user.logout()
            self.app.user.login_as_customer(user_name=user['user_name'], password=user['password'])

    def enter_unit_page_iframe(self):
        with allure.step('Enter unit_page iframe'):
            iframe = self.find_elements(".//iframe[@name='unit_page']")
            assert len(iframe) == 1, "iframe 'unit_page' not found"
            self.app.navigation.switch_to_frame(iframe[0])

    def enter_shapes_iframe(self):
        with allure.step('Enter shapes iframe'):
            iframe = self.find_elements(".//iframe[contains(@src, 'Shapes')]")
            assert len(iframe) == 1, "'Shapes' iframe not found"
            self.app.navigation.switch_to_frame(iframe[0])

    def scroll_to_secure_img(self):
        with allure.step('Scroll to the img with secure src'):
            click_rebrand_popover(self.driver)
            secure_image = self.find_elements("//img[contains(@src, 'secure')]")
            assert len(secure_image) == 1, "'img' secure element not found"
            src = secure_image[0].get_attribute('src')
            js_utils.scroll_to_element(self.driver, secure_image[0])
            return src


    def scroll_to_canvas(self):
        with allure.step('Scroll to the canvas with secure src'):
            canvas_div = self.find_elements("//div[@class='canvas-container']")
            assert len(canvas_div) == 1, "Canvas div element not found"
            js_utils.scroll_to_element(self.driver, canvas_div[0])
    
    def verify_image(self, tag='img'):
        with allure.step(f'Compare screenshot to baseline {tag}'):
            fp = selenium_utils.create_screenshot(self.driver, name='temp')
            score = compare_images(baseline_screenshots[tag], fp)
            os.remove(fp)
            assert score > 0.6, f"Screenshot of {tag} does not match the baseline"
