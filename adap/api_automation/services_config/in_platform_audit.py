import allure
import logging

from adap.api_automation.utils.data_util import *
from adap.api_automation.utils.http_util import HttpMethod
from adap.api_automation.services_config.endpoints.audit_service_endpoints import *

LOGGER = logging.getLogger(__name__)


class IPA_API:
    def __init__(self, api_key, custom_url=None, payload=None, env=None):
        self.api_key = api_key
        self.payload = payload

        if env is None and custom_url is None: env = pytest.env
        self.env = env
        if custom_url is not None:
            self.url = custom_url
        else:
            self.url = URL.format(env)

        self.service = HttpMethod(self.url, self.payload)

    @allure.step
    def get_status_info(self, job_id):
        return self.service.get(JOB_STATUS.format(job_id=job_id))

    @allure.step
    def get_aggregations_distribution(self, job_id):
        return self.service.get(GET_AGGREGATIONS_DISTRIBUTION.format(job_id=job_id))

    @allure.step
    def get_job_and_field_accuracy(self, job_id):
        return self.service.get(JOB_ACCURACY.format(job_id=job_id))

    @allure.step
    def post_job_and_field_accuracy(self, job_id, data):
        headers = {
            'content-type': 'application/json',
            'accept': 'application/json'
        }
        return self.service.post(JOB_ACCURACY.format(job_id=job_id),  headers=headers, data=json.dumps(data))

    @allure.step
    def get_audit_info_for_unit(self, job_id, unit_id):
        return self.service.get(AUDIT_UNIT.format(job_id=job_id, unit_id=unit_id))

    @allure.step
    def search_unit_for_audit(self, job_id, data):
        headers = {
            'content-type': 'application/json',
            'accept': 'application/json'
        }
        return self.service.post(SEARCH_UNIT.format(job_id=job_id), headers=headers, data=json.dumps(data))

    @allure.step
    def generate_aggregation(self, job_id):
        return self.service.post(GENERATE_AGGREGATIONS.format(job_id=job_id))

    @allure.step
    def add_audit(self, job_id, unit_id, data):
        headers = {
            'content-type': 'application/json',
            'accept': 'application/json'
        }
        return self.service.put(AUDIT_UNIT.format(job_id=job_id, unit_id=unit_id), headers=headers, data=json.dumps(data))

    @allure.step
    def generate_ipa_report(self, job_id):
        return self.service.post(REPORT.format(job_id=job_id))

    @allure.step
    def get_ipa_report(self, job_id, report_version):
        return self.service.get(REPORT_VERSION.format(job_id=job_id, report_version=report_version))

    @allure.step
    def cancel_aggregations(self, job_id):
        return self.service.post(CANCEL_AGGREGATIONS.format(job_id=job_id))

    @allure.step
    def get_all_judgment(self, job_id, unit_id):
        return self.service.get(ALL_JUDGMENTS.format(job_id=job_id, unit_id=unit_id))

    @allure.step
    def get_contributors(self, job_id, question_name):
        return self.service.get(CONTRIBUTORS.format(job_id=job_id, question_name=question_name))

    @allure.step
    def wait_until_regenerate_aggregation(self, status, job_id, max_wait=120):
        interval = 1
        _c = 0
        while _c < max_wait:
            res = self.get_status_info(job_id)
            completed_status = res.json_response
            logging.info(completed_status)
            if status not in completed_status:
                break
            else:
                _c += interval
        else:
            msg = f'Max wait time reached, ' \
                  f'job {job_id} status: {status}, ' \
                  f'present in : {completed_status}'
            raise Exception(msg)
