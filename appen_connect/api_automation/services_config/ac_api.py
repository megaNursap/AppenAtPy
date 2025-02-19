import json

import allure
import pytest

from appen_connect.api_automation.services_config.endpoints.ac_api import *
from appen_connect.ui_automation.service_config.project.project_helper import generate_project_name
from adap.api_automation.utils.http_util import HttpMethod
from appen_connect.api_automation.services_config.endpoints.roster_tracker import WORKERS_EXPORT_ALL, WORKERS_EXPORT, \
    METRICS, WORKERS, MARKETS


def get_valid_cookies(app, user_name, user_password):
    app.ac_user.login_as(user_name=user_name, password=user_password)
    app.navigation.click_link('Partner Home')
    # app.ac_user.select_customer('Appen Internal')
    flat_cookie_dict = {seleniumCookie['name']: seleniumCookie['value'] for seleniumCookie in app.driver.get_cookies()}
    return flat_cookie_dict


@allure.step
def create_new_random_project(api):
    project_name = generate_project_name()
    payload = {
        "alias": project_name[1],
        "name": project_name[0],
        "taskVolume": "VERY_LOW",
        "workType": "LINGUISTICS",
        "description": project_name[0],
        "projectType": "Regular",
        "rateType": "HOURLY",
        "customerId": 53
    }
    res = api.create_project(payload=payload)
    res.assert_response_status(201)
    return {"input": payload,
            "output": res.json_response}


class AC_API:

    def __init__(self, cookies=None, payload=None, custom_url=None, headers=None, env=None, version='v2'):
        self.payload = payload
        self.cookies = cookies

        if env is None and custom_url is None:  env = pytest.env
        self.env = env

        if custom_url is not None:
            self.url = custom_url
        else:
            self.url = URL(env=pytest.env).format(version=version)

        if not headers:
            self.headers = {
                'accept': 'application/json',
                'Content-Type': 'text/plain'
            }

        self.service = HttpMethod(self.url, self.payload)

    @allure.step
    def get_session(self, cookies=None):
        if not cookies:
            cookies = self.cookies
        res = self.service.get(AUTH, headers={'Content-Type': 'text/plain'}, cookies=cookies, ep_name=AUTH)
        return res

    @allure.step
    def get_session_me(self, cookies=None):
        if not cookies:
            cookies = self.cookies
        res = self.service.get(AUTH_ME, headers=self.headers, cookies=cookies, ep_name=AUTH_ME)
        return res

    @allure.step
    def get_project_status(self, cookies=None):
        if not cookies:
            cookies = self.cookies
        res = self.service.get(PROJECT_STATUS, headers=self.headers, cookies=cookies, ep_name=PROJECT_STATUS)
        return res

    @allure.step
    def get_business_units(self, cookies=None):
        if not cookies:
            cookies = self.cookies
        res = self.service.get(BUSINESS_UNITS, headers=self.headers, cookies=cookies, ep_name=BUSINESS_UNITS)
        return res

    @allure.step
    def get_countries(self, exclude_wildcard=None, language=None, cookies=None):
        if not cookies:
            cookies = self.cookies
        _url = COUNTRIES
        if exclude_wildcard:
            _url += "/?excludeWildcard={}".format(exclude_wildcard)
        if language:
            _add = "&" if exclude_wildcard else "/?"
            _url += _add + "language={}".format(language)

        res = self.service.get(_url, headers=self.headers, cookies=cookies, ep_name=COUNTRIES)
        return res

    @allure.step
    def get_states(self, country_id, include_territories, cookies=None):
        if not cookies:
            cookies = self.cookies
        res = self.service.get(STATES.format(country_id=country_id, include_territories=include_territories),
                               headers=self.headers, cookies=cookies, ep_name=STATES)
        return res

    @allure.step
    def get_external_systems(self, cookies=None):
        if not cookies:
            cookies = self.cookies
        res = self.service.get(EXTERNAL_SYSTEMS, headers=self.headers, cookies=cookies, ep_name=EXTERNAL_SYSTEMS)
        return res

    @allure.step
    def get_groups(self, by_current_customer=None, customer_id=None, cookies=None):
        if not cookies:
            cookies = self.cookies
        _url = GROUPS
        if by_current_customer:
            _url = GROUPS + "?byCurrentCustomer={}".format(by_current_customer)
        if customer_id:
            _url = GROUPS + "?customerId={}".format(customer_id)
        res = self.service.get(_url, headers=self.headers, cookies=cookies, ep_name=GROUPS)
        return res

    @allure.step
    def get_hiring_target(self, project_id, cookies=None):
        if not cookies:
            cookies = self.cookies
        res = self.service.get(HIRING_TARGET + "?projectId={}".format(project_id), headers=self.headers,
                               cookies=cookies, ep_name=HIRING_TARGET)
        return res

    @allure.step
    def add_hiring_target(self, payload, cookies=None):
        if not cookies:
            cookies = self.cookies
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }
        res = self.service.post(HIRING_TARGET, headers=headers, cookies=cookies, data=json.dumps(payload),
                                ep_name=HIRING_TARGET)
        return res

    @allure.step
    def get_projects(self, params=None, cookies=None):
        if not cookies:
            cookies = self.cookies

        res = self.service.get(PROJECTS, params=params, headers=self.headers, cookies=cookies, ep_name=PROJECTS)
        return res

    @allure.step
    def create_project(self, payload=None, cookies=None):
        if not cookies:
            cookies = self.cookies

        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }
        res = self.service.post(PROJECTS, headers=headers, cookies=cookies, data=json.dumps(payload),
                                ep_name=PROJECTS)
        return res

    @allure.step
    def get_project_by_id(self, id, cookies=None):
        if not cookies:
            cookies = self.cookies
        res = self.service.get(PROJECTS + "/{id}".format(id=id), headers=self.headers, cookies=cookies,
                               ep_name=PROJECTS)
        return res

    @allure.step
    def update_project(self, id, payload, cookies=None):
        if not cookies:
            cookies = self.cookies
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }
        res = self.service.patch((PROJECTS + "/{id}".format(id=id)), data=json.dumps(payload), headers=headers,
                                 cookies=cookies, ep_name=PROJECTS)
        return res

    @allure.step
    def create_pay_rate(self, payload, cookies=None):
        if not cookies:
            cookies = self.cookies
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }
        res = self.service.post(PAY_RATES.format(id=id), data=json.dumps(payload), headers=headers, cookies=cookies,
                                ep_name=PAY_RATES)
        return res

    @allure.step
    def get_task_volumes(self, cookies=None):
        if not cookies:
            cookies = self.cookies
        res = self.service.get(TASK_VOLUMES, headers=self.headers, cookies=cookies, ep_name=TASK_VOLUMES)
        return res

    @allure.step
    def get_locale_tenants(self, id, cookies=None):
        if not cookies:
            cookies = self.cookies
        res = self.service.get(LOCALE_TENANTS + "?projectId={id}".format(id=id), headers=self.headers, cookies=cookies,
                               ep_name=LOCALE_TENANTS)
        return res

    @allure.step
    def create_locale_tenant(self, payload, cookies=None):
        if not cookies:
            cookies = self.cookies
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }
        res = self.service.post(LOCALE_TENANTS, data=json.dumps(payload), headers=headers, cookies=cookies,
                                ep_name=LOCALE_TENANTS)
        return res

    @allure.step
    def update_locale_tenants(self, tenant_id, payload, cookies=None):
        if not cookies:
            cookies = self.cookies
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }
        res = self.service.put((LOCALE_TENANTS + "/{id}".format(id=tenant_id)), data=json.dumps(payload),
                               headers=headers, cookies=cookies, ep_name=LOCALE_TENANTS)
        return res

    @allure.step
    def delete_locale_tenant(self, tenant_id, cookies=None):
        if not cookies:
            cookies = self.cookies
        headers = {
            'accept': '*/*'
        }
        res = self.service.delete((LOCALE_TENANTS + "/{id}".format(id=tenant_id)), headers=headers, cookies=cookies,
                                  ep_name=LOCALE_TENANTS)
        return res

    @allure.step
    def get_languages(self, cookies=None):
        if not cookies:
            cookies = self.cookies
        res = self.service.get(LANGUAGES, headers=self.headers, cookies=cookies, ep_name=LANGUAGES)
        return res

    @allure.step
    def get_project_pages(self, project_id, cookies=None):
        if not cookies:
            cookies = self.cookies
        res = self.service.get(PROJECT_PAGES + "?projectId={id}".format(id=project_id), headers=self.headers,
                               cookies=cookies, ep_name=LANGUAGES)
        return res

    @allure.step
    def get_language_fluency_level(self, cookies=None):
        if not cookies:
            cookies = self.cookies
        res = self.service.get(LANGUAGE_FLUENCY_LEVEL, headers=self.headers, cookies=cookies,
                               ep_name=LANGUAGE_FLUENCY_LEVEL)
        return res

    @allure.step
    def update_hiring_targets(self, target_id, payload, cookies=None):
        if not cookies:
            cookies = self.cookies
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }
        res = self.service.put((HIRING_TARGET + "/{id}".format(id=target_id)), data=json.dumps(payload),
                               headers=headers, cookies=cookies, ep_name=HIRING_TARGET)
        return res

    @allure.step
    def delete_hiring_target(self, target_id, cookies=None):
        if not cookies:
            cookies = self.cookies
        headers = {
            'accept': '*/*'
        }
        res = self.service.delete((HIRING_TARGET + "/{id}".format(id=target_id)), headers=headers, cookies=cookies,
                                  ep_name=HIRING_TARGET)
        return res

    @allure.step
    def get_pay_rates(self, project_id, cookies=None):
        if not cookies:
            cookies = self.cookies
        res = self.service.get(PAY_RATES + "?projectId={id}".format(id=project_id), headers=self.headers,
                               cookies=cookies,
                               ep_name=PAY_RATES)
        return res

    @allure.step
    def get_pay_rates_by_id(self, id, cookies=None):
        if not cookies:
            cookies = self.cookies
        res = self.service.get(PAY_RATES + "/{id}".format(id=id), headers=self.headers, cookies=cookies,
                               ep_name=PAY_RATES)
        return res

    @allure.step
    def update_pay_rate(self, rate_id, payload, cookies=None):
        if not cookies:
            cookies = self.cookies
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }
        res = self.service.patch((PAY_RATES + "/{id}".format(id=rate_id)), data=json.dumps(payload),
                                 headers=headers, cookies=cookies, ep_name=PAY_RATES)
        return res

    @allure.step
    def delete_pay_rate(self, id, cookies=None):
        if not cookies:
            cookies = self.cookies
        headers = {
            'accept': '*/*'
        }
        res = self.service.delete((PAY_RATES + "/{id}".format(id=id)), headers=headers, cookies=cookies,
                                  ep_name=PAY_RATES)
        return res

    @allure.step
    def get_task_types(self, cookies=None):
        if not cookies:
            cookies = self.cookies
        res = self.service.get(TASK_TYPES, headers=self.headers, cookies=cookies, ep_name=TASK_TYPES)
        return res

    @allure.step
    def get_rate_types(self, cookies=None):
        if not cookies:
            cookies = self.cookies
        res = self.service.get(RATE_TYPES, headers=self.headers, cookies=cookies, ep_name=RATE_TYPES)
        return res

    @allure.step
    def get_team_types(self, cookies=None):
        if not cookies:
            cookies = self.cookies
        res = self.service.get(TEAM_TYPES, headers=self.headers, cookies=cookies, ep_name=TEAM_TYPES)
        return res

    @allure.step
    def get_tenants(self, country=None, cookies=None):
        if not cookies:
            cookies = self.cookies
        if country:
            res = self.service.get(TENANTS + '?country={}'.format(country), headers=self.headers, cookies=cookies,
                                   ep_name=TENANTS)
        else:
            res = self.service.get(TENANTS, headers=self.headers, cookies=cookies, ep_name=TENANTS)

        return res

    @allure.step
    def get_users(self, user_type=None, cookies=None):
        if not cookies:
            cookies = self.cookies
        if user_type:
            res = self.service.get(USERS + '?type={}'.format(user_type), headers=self.headers, cookies=cookies,
                                   ep_name=USERS)
        else:
            res = self.service.get(USERS, headers=self.headers, cookies=cookies, ep_name=USERS)
        return res

    @allure.step
    def get_work_types(self, cookies=None):
        if not cookies:
            cookies = self.cookies
        res = self.service.get(WORK_TYPES, headers=self.headers, cookies=cookies, ep_name=WORK_TYPES)
        return res

    @allure.step
    def get_bpm_qualification_steps(self, bpm_type=None, cookies=None):
        if not cookies:
            cookies = self.cookies
        if bpm_type:
            res = self.service.get(BPM_QUALIFICATION_STEPS + '?type={}'.format(bpm_type), headers=self.headers, cookies=cookies,
                                   ep_name=BPM_QUALIFICATION_STEPS)
        else:
            res = self.service.get(BPM_QUALIFICATION_STEPS, headers=self.headers, cookies=cookies, ep_name=BPM_QUALIFICATION_STEPS)
        return res

    @allure.step
    def get_bpm_qualification_step(self, step_id, cookies=None):
        if not cookies:
            cookies = self.cookies
        res = self.service.get(BPM_QUALIFICATION_STEPS + '/{}'.format(step_id), headers=self.headers, cookies=cookies,
                               ep_name=BPM_QUALIFICATION_STEPS)
        return res

    @allure.step
    def get_bpm_registration_steps(self, bpm_type=None, cookies=None):
        if not cookies:
            cookies = self.cookies
        if bpm_type:
            res = self.service.get(BPM_REGISTRATION_STEPS + '?type={}'.format(bpm_type), headers=self.headers,
                                   cookies=cookies,
                                   ep_name=BPM_REGISTRATION_STEPS)
        else:
            res = self.service.get(BPM_REGISTRATION_STEPS, headers=self.headers, cookies=cookies,
                                   ep_name=BPM_REGISTRATION_STEPS)
        return res

    @allure.step
    def get_bpm_registration_step(self, step_id, cookies=None):
        if not cookies:
            cookies = self.cookies
        res = self.service.get(BPM_REGISTRATION_STEPS + '/{}'.format(step_id), headers=self.headers, cookies=cookies,
                               ep_name=BPM_REGISTRATION_STEPS)
        return res

    @allure.step
    def get_qualification_process_types(self,cookies=None):
        if not cookies:
            cookies = self.cookies
        res = self.service.get(QUALIFICATION_PROCESS_TYPES, headers=self.headers, cookies=cookies,
                               ep_name=QUALIFICATION_PROCESS_TYPES)
        return res

    @allure.step
    def get_qualification_process_projects(self, id, cookies=None):
        if not cookies:
            cookies = self.cookies
        res = self.service.get(QUALIFICATION_PROCESS_PROJECTS.format(id=id), headers=self.headers, cookies=cookies,
                               ep_name=QUALIFICATION_PROCESS_PROJECTS)
        return res

    @allure.step
    def get_qualification_processes(self, cookies=None):
        if not cookies:
            cookies = self.cookies
        res = self.service.get(QUALIFICATION_PROCESS, headers=self.headers, cookies=cookies,
                               ep_name=QUALIFICATION_PROCESS)
        return res

    @allure.step
    def create_qualification_processes(self, payload, cookies=None):
        if not cookies:
            cookies = self.cookies
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }
        res = self.service.post(QUALIFICATION_PROCESS, data=json.dumps(payload), headers=headers, cookies=cookies,
                                ep_name=QUALIFICATION_PROCESS)
        return res

    @allure.step
    def get_qualification_process_by_id(self, process_id, cookies=None):
        if not cookies:
            cookies = self.cookies
        res = self.service.get(QUALIFICATION_PROCESS + '/{}'.format(process_id), headers=self.headers, cookies=cookies,
                               ep_name=QUALIFICATION_PROCESS)
        return res

    @allure.step
    def update_qualification_process_by_id(self, process_id, payload, cookies=None):
        if not cookies:
            cookies = self.cookies
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }
        res = self.service.put((QUALIFICATION_PROCESS + "/{id}".format(id=process_id)), data=json.dumps(payload),
                               headers=headers, cookies=cookies, ep_name=QUALIFICATION_PROCESS)
        return res

    @allure.step
    def get_qualification_process_by_id(self, process_id, cookies=None):
        if not cookies:
            cookies = self.cookies
        res = self.service.get(QUALIFICATION_PROCESS + '/{}'.format(process_id), headers=self.headers, cookies=cookies,
                               ep_name=QUALIFICATION_PROCESS)
        return res

    @allure.step
    def get_projects_by_qualification_process_id(self, process_id, cookies=None):
        if not cookies:
            cookies = self.cookies
        res = self.service.get(QUALIFICATION_PROCESS_PROJECTS.format(id=process_id), headers=self.headers, cookies=cookies,
                               ep_name=QUALIFICATION_PROCESS_PROJECTS)
        return res

    @allure.step
    def get_projects_by_registration_process_id(self, process_id, cookies=None):
        if not cookies:
            cookies = self.cookies
        res = self.service.get(REGISTRATION_PROCESS_PROJECTS.format(id=process_id), headers=self.headers,
                               cookies=cookies,
                               ep_name=REGISTRATION_PROCESS_PROJECTS)
        return res

    @allure.step
    def get_registration_process_types(self, cookies=None):
        if not cookies:
            cookies = self.cookies
        res = self.service.get(REGISTRATION_PROCESS_TYPES, headers=self.headers, cookies=cookies,
                               ep_name=REGISTRATION_PROCESS_TYPES)
        return res

    @allure.step
    def get_registration_processes(self, cookies=None):
        if not cookies:
            cookies = self.cookies
        res = self.service.get(REGISTRATION_PROCESS, headers=self.headers, cookies=cookies,
                               ep_name=REGISTRATION_PROCESS)
        return res

    @allure.step
    def create_registration_processes(self, payload, cookies=None):
        if not cookies:
            cookies = self.cookies
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }
        res = self.service.post(REGISTRATION_PROCESS, data=json.dumps(payload), headers=headers, cookies=cookies,
                                ep_name=REGISTRATION_PROCESS)
        return res

    @allure.step
    def get_registration_process_by_id(self, process_id, cookies=None):
        if not cookies:
            cookies = self.cookies
        res = self.service.get(REGISTRATION_PROCESS + '/{}'.format(process_id), headers=self.headers, cookies=cookies,
                               ep_name=REGISTRATION_PROCESS)
        return res

    @allure.step
    def update_registration_process_by_id(self, process_id, payload, cookies=None):
        if not cookies:
            cookies = self.cookies
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }
        res = self.service.put((REGISTRATION_PROCESS + "/{id}".format(id=process_id)), data=json.dumps(payload),
                               headers=headers, cookies=cookies, ep_name=REGISTRATION_PROCESS)
        return res

    @allure.step
    def get_demographics_requirements(self, project_id=None, hiring_target_id=None, cookies=None):
        if not cookies:
            cookies = self.cookies
        _url = DEMOGRAPHICS_REQUIREMENTS
        if project_id:
            _url += "/?projectId={}".format(project_id)
        if hiring_target_id:
            _add = "&" if project_id else "/?"
            _url += _add + "hiringTargetId={}".format(hiring_target_id)
        res = self.service.get(_url, headers=self.headers, cookies=cookies, ep_name=DEMOGRAPHICS_REQUIREMENTS)
        return res

    @allure.step
    def create_demographics_requirements(self, payload, cookies=None):
        if not cookies:
            cookies = self.cookies
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }
        res = self.service.post(DEMOGRAPHICS_REQUIREMENTS, data=json.dumps(payload), headers=headers, cookies=cookies,
                                ep_name=DEMOGRAPHICS_REQUIREMENTS)
        return res

    @allure.step
    def update_demographics_requirements(self, payload, cookies=None):
        if not cookies:
            cookies = self.cookies
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }
        res = self.service.put(DEMOGRAPHICS_REQUIREMENTS, data=json.dumps(payload), headers=headers, cookies=cookies, ep_name=REGISTRATION_PROCESS)
        return res

    @allure.step
    def get_demographics_metrics(self, generalMetrics='false', project_id=None, hiring_target_id=None, cookies=None):
        if not cookies:
            cookies = self.cookies
        _url = DEMOGRAPHICS_METRICS.format(generalMetrics)
        if project_id:
            _url += "&projectId={}".format(project_id)
        if hiring_target_id:
            _url += "&hiringTargetId={}".format(hiring_target_id)
        res = self.service.get(_url, headers=self.headers, cookies=cookies, ep_name=DEMOGRAPHICS_METRICS)
        return res

    @allure.step
    def get_demographics_parameters(self, cookies=None):
        if not cookies:
            cookies = self.cookies
        res = self.service.get(DEMOGRAPHICS_PARAMETERS, headers=self.headers, cookies=cookies,
                               ep_name=DEMOGRAPHICS_PARAMETERS)
        return res

    @allure.step
    def delete_demographics_requirements(self, project_id=None, hiring_target_id=None, cookies=None):
        if not cookies:
            cookies = self.cookies
        _url = DEMOGRAPHICS_REQUIREMENTS
        if project_id:
            _url += "/?projectId={}".format(project_id)
        if hiring_target_id:
            _add = "&" if project_id else "/?"
            _url += _add + "hiringTargetId={}".format(hiring_target_id)
        res = self.service.delete(_url, headers=self.headers, cookies=cookies, ep_name=DEMOGRAPHICS_REQUIREMENTS)
        return res


    @allure.step
    def update_project_status(self, id, payload, cookies=None):
        if not cookies:
            cookies = self.cookies
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }
        res = self.service.put(STATUS.format(id=id), data=json.dumps(payload),
                               headers=headers, cookies=cookies, ep_name=STATUS)
        return res

    @allure.step
    def update_invoice_configuration(self, id, payload, cookies=None):
        if not cookies:
            cookies = self.cookies
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }
        res = self.service.put(INVOICE_CONFIGURATION.format(id=id), data=json.dumps(payload),
                               headers=headers, cookies=cookies, ep_name=INVOICE_CONFIGURATION)
        return res

    @allure.step
    def get_invoice_configuration(self, id, cookies=None):
        if not cookies:
            cookies = self.cookies
        res = self.service.get(INVOICE_CONFIGURATION.format(id=id), headers=self.headers, cookies=cookies,
                               ep_name=INVOICE_CONFIGURATION)
        return res

    @allure.step
    def get_experiments_status(self, cookies=None):
        if not cookies:
            cookies = self.cookies
        res = self.service.get(EXPERIMENT_STATUS, headers=self.headers, cookies=cookies,
                               ep_name=EXPERIMENT_STATUS)
        return res

    @allure.step
    def get_experiments_for_project(self, id, access='true', cookies=None):
        if not cookies:
            cookies = self.cookies
        res = self.service.get(EXPERIMENTS+"?projectId={id}&accessHolder={access}".format(id=id, access=access), headers=self.headers, cookies=cookies,
                               ep_name=EXPERIMENTS)
        return res

    @allure.step
    def update_experiment(self, id, payload, cookies=None):
        if not cookies:
            cookies = self.cookies
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }
        res = self.service.put(EXPERIMENT.format(id=id), data=json.dumps(payload),
                               headers=headers, cookies=cookies, ep_name=EXPERIMENT)
        return res


    @allure.step
    def create_experiment_group(self, id, payload, cookies=None):
        if not cookies:
            cookies = self.cookies
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }
        res = self.service.post(EXPERIMENT_GROUPS.format(id=id), data=json.dumps(payload),
                               headers=headers, cookies=cookies, ep_name=EXPERIMENT_GROUPS)
        return res


    @allure.step
    def get_experiments_groups(self, id, cookies=None):
        if not cookies:
            cookies = self.cookies
        res = self.service.get(EXPERIMENT_GROUPS.format(id=id), headers=self.headers, cookies=cookies,
                               ep_name=EXPERIMENT_GROUPS)
        return res


    @allure.step
    def update_experiment_group(self, id, payload, cookies=None):
        if not cookies:
            cookies = self.cookies
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }
        res = self.service.put(EXPERIMENT_GROUPS.format(id=id), data=json.dumps(payload),
                               headers=headers, cookies=cookies, ep_name=EXPERIMENT_GROUPS)
        return res


    @allure.step
    def get_resource_mappings(self, id, cookies=None):
        if not cookies:
            cookies = self.cookies
        res = self.service.get(RESOURCE_MAPPINGS.format(id=id), headers=self.headers, cookies=cookies,
                               ep_name=RESOURCE_MAPPINGS)
        return res

    @allure.step
    def get_resource_quizzes(self, cookies=None):
        if not cookies:
            cookies = self.cookies
        res = self.service.get(QUIZZES, headers=self.headers, cookies=cookies,
                               ep_name=QUIZZES)
        return res

    @allure.step
    def get_resource_survey(self, cookies=None):
        if not cookies:
            cookies = self.cookies
        res = self.service.get(SURVEY, headers=self.headers, cookies=cookies,
                               ep_name=SURVEY)
        return res

    @allure.step
    def get_resource_documents(self, cookies=None):
        if not cookies:
            cookies = self.cookies
        res = self.service.get(DOCUMENTS, headers=self.headers, cookies=cookies,
                               ep_name=DOCUMENTS)
        return res

    @allure.step
    def get_resource_academies(self, cookies=None):
        if not cookies:
            cookies = self.cookies
        res = self.service.get(ACADEMIES, headers=self.headers, cookies=cookies,
                               ep_name=ACADEMIES)
        return res

    @allure.step
    def post_resource_mappings(self, id, payload, cookies=None):
        if not cookies:
            cookies = self.cookies
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }
        res = self.service.post(RESOURCE_MAPPINGS.format(id=id), data=json.dumps(payload),
                               headers=headers, cookies=cookies, ep_name=RESOURCE_MAPPINGS)
        return res


    @allure.step
    def update_resource_mappings(self, id, resourceid, payload, cookies=None):
        if not cookies:
            cookies = self.cookies
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }
        res = self.service.put(RESOURCE_MAPPINGS_EDIT.format(id=id, resourceid=resourceid), data=json.dumps(payload),
                               headers=headers, cookies=cookies, ep_name=RESOURCE_MAPPINGS_EDIT)
        return res


    @allure.step
    def get_dc_consent_form(self, id, cookies=None):
        if not cookies:
            cookies = self.cookies
        res = self.service.get(DC_CONSENT_FORMS.format(projectId=id), headers=self.headers, cookies=cookies,
                               ep_name=DC_CONSENT_FORMS)
        return res

    @allure.step
    def create_dc_consent_form(self, id, payload, cookies=None):
        if not cookies:
            cookies = self.cookies
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }
        res = self.service.post(DC_CONSENT_FORMS.format(projectId=id), data=json.dumps(payload), headers=headers,
                                cookies=cookies, ep_name=DC_CONSENT_FORMS)
        return res

    @allure.step
    def update_dc_consent_form(self, id, payload, cookies=None):
        if not cookies:
            cookies = self.cookies
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }
        res = self.service.post(DC_VERSION.format(dc_id=id), data=json.dumps(payload), headers=headers,
                                cookies=cookies, ep_name=DC_VERSION)
        return res

    @allure.step
    def get_pii_data(self, cookies=None):
        if not cookies:
            cookies = self.cookies
        res = self.service.get(PII_DATA, headers=self.headers, cookies=cookies, ep_name=PII_DATA)
        return res

    @allure.step
    def get_appen_entities(self, cookies=None):
        if not cookies:
            cookies = self.cookies
        res = self.service.get(APPEN_ENTITIES, headers=self.headers, cookies=cookies, ep_name=APPEN_ENTITIES)
        return res


