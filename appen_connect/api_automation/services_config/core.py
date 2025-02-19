import appen_connect.api_automation.services_config.endpoints.core as ep
from adap.api_automation.utils.http_util import HttpMethod
from bs4 import BeautifulSoup

form_headers = {
    'Accept': '*/*',
    'Content-Type': 'application/x-www-form-urlencoded',
}


class Core:
    def __init__(self, env, service=None, session=True):
        self.url = ep.URL(env=env)
        self.service = HttpMethod(base_url=self.url, session=session)

    def sign_in(self, username, password):
        login_page = self.service.get(ep.LOGIN, ep_name=ep.LOGIN)
        soup = BeautifulSoup(login_page.text, 'html.parser')
        sourcePage_val = soup.find('input', {'name': '_sourcePage'}).get('value')
        fp_val = soup.find('input', {'name': '__fp'}).get('value')
        signin_form_data = {
            'ruri': None,
            'timeZoneIdentifier': 'America/Los_Angeles',
            'username': username,
            'password': password,
            'code': None,
            'login': 'Login',
            '_sourcePage': sourcePage_val,
            '__fp': fp_val
        }
        sign_in = self.service.post(
            ep.LOGIN,
            allow_redirects=True,
            headers=form_headers,
            data=signin_form_data,
            ep_name=ep.LOGIN
            )
        return sign_in

    def sign_out(self):
        return self.service.get(
            ep.LOGOUT,
            allow_redirects=True,
            ep_name=ep.LOGOUT
            )

    def sign_in_sso(self, username, password, credentialId=None):
        """
        Sign in using SSO (Keycloak)
        """
        login_page = self.service.get(
            ep.LOGIN,
            ep_name=ep.LOGIN,
            allow_redirects=True)
        assert login_page.status_code == 200, f"{login_page.status_code},"\
                                              f"{login_page.text}"
        soup = BeautifulSoup(login_page.text, 'html.parser')
        kc_form = soup.find('form', {'id': 'kc-form-login'})
        assert kc_form is not None, "Keycloack form not found: "\
                                    f"{login_page.url}: {soup}"
        kc_login_url = kc_form.get('action')
        assert kc_login_url is not None, "Keycloack action not found: "\
                                         f"{soup}"
        _base_url = self.service.base_url
        self.service.base_url = ''
        kc_login = self.service.post(
            kc_login_url,
            headers=form_headers,
            data={
                'username': username,
                'password': password,
                'credentialId': credentialId
            },
            allow_redirects=True,
            ep_name="identity service authentication"
            )
        self.service.base_url = _base_url
        return kc_login

    def get_vendor(self, user_id):
        return self.service.get(
            ep.VENDOR_VIEW.format(user_id=user_id),
            ep_name=ep.VENDOR_VIEW
            )

    def impersonate(self, user_id):
        return self.service.get(
            ep.IMPERSONATE.format(user_id=user_id),
            allow_redirects=True,
            ep_name=ep.IMPERSONATE
            )

    def get_vendor_project(self, project_id):
        return self.service.get(
            ep.VENDOR_TASK_VIEW.format(project_id=project_id),
            ep_name=ep.VENDOR_TASK_VIEW
            )

    def get_timesheets(self, project_id):
        return self.service.get(
            f"{ep.ACAN_TIMESHEETS}?view=&project.id={project_id}",
            ep_name=ep.ACAN_TIMESHEETS
            )

    def update_timesheets(self, _id, project_id, description=None):
        """
        Some of the available ids:
        0: 'Finish your Day'
        1: 'Lunch'
        13: 'QA Sampling'
        17: 'Break'
        20: 'Team Meeting'
        """
        update_url = f"{ep.ACAN_TIMESHEETS}?ajaxUpdate="
        update_form_data = {
            'id': _id,
            'projectId': project_id,
            'description': description
        }
        resp = self.service.post(
            update_url,
            allow_redirects=True,
            headers=form_headers,
            data=update_form_data,
            ep_name=update_url
            )
        return resp

    def full_stop_timesheets(self, project_id):
        stop_url = f"{ep.ACAN_TIMESHEETS}?ajaxStop="
        update_url = f"{ep.ACAN_TIMESHEETS}?ajaxUpdate="
        confirm_stop_url = f"{ep.ACAN_TIMESHEETS}?ajaxConfirmStop="
        stop = self.service.post(
            stop_url,
            headers=form_headers,
            data={
                'id': 0,
                'projectId': project_id
            },
            ep_name=stop_url)
        assert stop.status_code == 200, 'Stop request failed: '\
                                        f'{stop.status_code}::{stop.text}'
        update = self.service.post(
            update_url,
            headers=form_headers,
            data={
                'id': 0,
                'projectId': project_id,
                'description': None
            },
            ep_name=update_url)
        assert update.status_code == 200, 'Update request failed: '\
                                          f'{update.status_code}::{update.text}'
        confirm = self.service.post(
            confirm_stop_url,
            headers=form_headers,
            data={
                'id': 0,
                'projectId': project_id
            },
            ep_name=confirm_stop_url)
        return confirm
