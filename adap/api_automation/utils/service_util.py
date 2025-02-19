import pytest

from adap.api_automation.services_config.builder import Builder
import time
import logging

from adap.api_automation.services_config.quality_flow import QualityFlowApiProject
from adap.api_automation.services_config.workflow import Workflow
from adap.api_automation.services_config.mlapi import MLAPI
from adap.api_automation.utils.qf_elasticsearch_util import ElasticsearchQF, white_list

LOGGER = logging.getLogger(__name__)


def delete_jobs(jobs, env=None):
    """
    :param jobs:  dict - key:job_id, value:api_key
    """

    errors = []

    LOGGER.info(f"Jobs: {jobs} will be deleted")

    for id, api_key in jobs.items():

        _job = Builder(api_key, env=env)
        _job.job_id = id

        result_json_job_status = _job.get_json_job_status()
        status = result_json_job_status.json_response

        # retry in case of a gateway timeout error
        if 'error' in status:
            errors.append(status)
            if 'Gateway timeout' in status.get('error').get('message'):
                time.sleep(2)
                status = _job.get_json_job_status().json_response
            elif result_json_job_status.status_code == 404:
                LOGGER.info(f"Job id: {id} was not found on server, ignoring")
                continue
            else:
                raise Exception(f'Got unexpected error: {status}')

        if len(errors) > 2:
            raise Exception(f'{errors}\nGetting too many errors, exiting')

        state = status.get('state')
        if state:
            if state in ('running', 'paused'):
                _job.cancel_job()
                time.sleep(2)
        else:
            LOGGER.error(f"Could not get 'state' from {status}, continuing")
            continue

        # TODO replace to hard delete code reason="https://appen.atlassian.net/browse/QED-4381"
        api = Builder(api_key, env=env, api_version='v2')
        res = api.delete_job(id)
        if res.status_code == 200:
            print("Job %s was deleted" % id)
        else:
            print("Job - %s. Something went wrong. Error: %s" % (id, res.json_response))


def delete_wfs(wfs):
    print("WF to delete:", wfs)
    for id, api_key in wfs.items():

        _wf = Workflow(api_key)
        _wf.wf_id = id

        res = _wf.delete_wf(id)
        if res.status_code == 204:
            print("WF %s was deleted" % id)
        else:
            print("WF - %s. Something went wrong. Error: %s" % (id, res.json_response))


def delete_models(models):
    print(models)
    for model_id, user_id in models.items():

        _model = MLAPI(user_id)
        _model.model_id = model_id

        res = _model.delete_model(model_id)
        if res.status_code == 200:
            print("Model {id} was deleted".format(id=model_id))
        else:
            print("Model - {id}. Something went wrong. Error: {message}".format(id=model_id, message=res.json_response))


def delete_qf_projects_index(project_list):
    LOGGER.info(f"Deleting project index:{project_list} ")
    es = ElasticsearchQF(pytest.env)
    es.delete_indexes_for_projects(project_list)


def delete_qf_projects(project_list, delete_index=False):
    account_project_list = {}
    delete_index_projects = []

    for project in project_list:
        try:
            username = project['account']['name']
            password = project['account']['password']
            team_id = project['account']['team_id']
            account_project_list.setdefault(username, {'password': password,
                                                       'team_id': team_id,
                                                       'projects': []})

            current_list = account_project_list[username]['projects']
            current_list.append(project['project_id'])
            account_project_list[username]['projects'] = current_list

            if delete_index:
                delete_index_projects.append(project['project_id'])
        except:
            LOGGER.info(f"Error finding project data:{project} ")

    # delete projects
    for account, data in account_project_list.items():
        api = QualityFlowApiProject()
        api.get_valid_sid(account, data['password'])
        team_id = data['team_id']

        for project in data['projects']:
            if project in white_list[pytest.env]:
                continue

            # get project data
            res = api.get_project_details(project, team_id)
            if res.status_code == 200 and res.json_response.get('data', {}):
                version = res.json_response['data'].get('version')
                res = api.delete_project(project, team_id, version)
                if res.status_code == 200:
                    print("Project {id} was deleted".format(id=project))
                else:
                    print("Project - {id}. Something went wrong. Error: {message}".format(id=project,
                                                                                          message=res.json_response))

    if delete_index:
        delete_qf_projects_index(delete_index_projects)


