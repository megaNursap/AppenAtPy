from adap.api_automation.services_config import endpoints
from adap.api_automation.services_config.endpoints import client as ep
from adap.api_automation.utils.http_util import HttpMethod
from adap.settings import Config
from adap.api_automation.utils.helpers import find_authenticity_token


class Client:
    def __init__(self, **kwargs):
        self.env = kwargs.get('env') or Config.ENV
        self.job_id = kwargs.get('job_id')
        self.base_url = ep.URL.format(env=self.env)
        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
            "Content-Type": "application/x-www-form-urlencoded",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Pragma": "no-cache"
        }
        session = kwargs.get('session') or True
        self.service = kwargs.get('service') or HttpMethod(session=session)

    def get_new_session(self):
        url = self.base_url + ep.SESSIONS_NEW
        resp = self.service.get(url, headers=self.headers, ep_name=ep.SESSIONS_NEW)
        return resp

    def sign_in(self, email, password):
        new_session = self.get_new_session()
        token = find_authenticity_token(new_session.content)
        url = self.base_url + ep.SESSIONS
        payload = {
            'authenticity_token': token,
            'session[email]': email,
            'session[password]': password,
            'commit': 'Sign In',
        }
        session = self.service.post(
            url,
            allow_redirects=True,
            headers=self.headers,
            data=payload,
            cookies=new_session.cookies,
            ep_name=ep.SESSIONS
            )
        return session

    def get_job_api_settings(self, job_id=None):
        if job_id is None:
            job_id = self.job_id
        url = self.base_url + ep.SETTINGS_API.format(job_id=job_id)
        resp = self.service.get(
            url,
            headers=self.headers,
            ep_name=ep.SETTINGS_API)
        return resp

    def update_job_api_settings(self, data={}, job_id=None):
        """
        Parameters:
            data (dict):
                webhook_uri (str),
                alias (str),
                auto_order_timeout (int),
                bypass_estimated_fund_limit (bool),
                units_remain_finalized (bool),
                schedule_fifo (bool),
        """
        if job_id is None:
            job_id = self.job_id
        api_settings = self.get_job_api_settings(job_id)
        token = find_authenticity_token(api_settings.content)
        payload = [
            ('_method', 'patch'),
            ('commit', 'Save'),
            ('authenticity_token', token),
            ('job[webhook_uri]', data.get('webhook_uri')),
            ('job[alias]', data.get('alias')),
            ('job[auto_order]', 0),
            ('job[auto_order]', 1),  # enable auto ordering
            ('job[auto_order_timeout]', data.get('auto_order_timeout')),
            ('job[bypass_estimated_fund_limit]', 0),
            ('job[units_remain_finalized]', 0),
            ('job[schedule_fifo]', 0),
        ]
        if data.get('bypass_estimated_fund_limit'):
            payload.append(('job[bypass_estimated_fund_limit]', 1))
        if data.get('units_remain_finalized'):
            payload.append(('job[units_remain_finalized]', 1))
        if data.get('schedule_fifo'):
            payload.append(('job[schedule_fifo]', 1))
        url = self.base_url + ep.SETTINGS_API.format(job_id=job_id)
        resp = self.service.post(
            url,
            allow_redirects=True,
            headers=self.headers,
            data=payload,
            cookies=api_settings.cookies,
            ep_name=ep.SETTINGS_API
            )
        return resp

    def get_job_judgment_settings(self, job_id=None):
        if job_id is None:
            job_id = self.job_id
        url = self.base_url + ep.SETTINGS_JUDGMENTS.format(job_id=job_id)
        resp = self.service.get(
            url,
            headers=self.headers,
            ep_name=ep.SETTINGS_JUDGMENTS)
        return resp

    def update_job_judgment_settings(self, data: dict, job_id=None):
        """
        Parameters:
            data (dict):
                max_judgments_per_unit (int),
                min_unit_confidence (float),
                dynamic_judgment_fields (list),
        """
        if job_id is None:
            job_id = self.job_id
        judgment_settings = self.get_job_judgment_settings(job_id)
        token = find_authenticity_token(judgment_settings.content)
        payload = [
            ('_method', 'patch'),
            ('commit', 'Save'),
            ('authenticity_token', token),
            ('job[variable_judgments]', 0),
            ('job[variable_judgments]', 1),  # enable dynamic judgment collection
            ('job[max_judgments_per_unit]', data.get('max_judgments_per_unit')),
            ('job[min_unit_confidence]', data.get('min_unit_confidence')),
            ('job[dynamic_judgment_fields][]', None),
            *[('job[dynamic_judgment_fields][]', cf) for cf in data.get('dynamic_judgment_fields')]
        ]
        url = self.base_url + ep.SETTINGS_JUDGMENTS.format(job_id=job_id)
        resp = self.service.post(
            url,
            allow_redirects=True,
            headers=self.headers,
            data=payload,
            cookies=judgment_settings.cookies,
            ep_name=ep.SETTINGS_JUDGMENTS
            )
        return resp

    def get_unit(self, unit_id, job_id=None):
        if job_id is None:
            job_id = self.job_id
        url = self.base_url + ep.UNIT.format(
            job_id=job_id,
            unit_id=unit_id
        )
        resp = self.service.get(
            url,
            headers={}
        )
        return resp