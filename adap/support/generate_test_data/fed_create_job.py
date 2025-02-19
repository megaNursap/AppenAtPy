from urllib.parse import quote
from adap.api_automation.services_config.builder import Builder
from adap.e2e_automation.services_config.contributor_ui_support import generate_judgments_for_job
from adap.api_automation.utils.data_util import *
from adap.e2e_automation.services_config.job_api_support import create_job_from_config_api
from adap.e2e_automation.job_examples.simple_job import config

global USER_NAME, PASSWORD

sample_file = os.path.abspath(os.path.dirname(__file__)) + "/../../data/upload_data_files/workflows/shared-test-data-sets/customer_01_sample_22.csv"


def generate_job_link_fed(job_id, api_key, env):
    job = Builder(api_key, env='fed', env_fed=env)
    job.job_id = job_id

    res = job.get_json_job_status()
    res.assert_response_status(200)
    secret = quote(res.json_response['secret'], safe='')
    job_link = "https://app.%s.secure.cf3.us/worker-ui/channels/cf_internal/jobs/%s/work?secret=%s" % (env, res.json_response['id'], secret)
    print(f"Internal Job Link: %s" % job_link)

    return job_link


def create_and_launch_job(config, env, api_key):
    fed_url_api = "https://app.{}.secure.cf3.us/builder/v1".format(env)

    job_payload = {
        "key": api_key,
        "job": config['job']
    }
    new_job = Builder(api_key, custom_url=fed_url_api, api_version='v1', payload=job_payload, env_fed='qe83')

    res = new_job.create_job()
    assert res.status_code == 200
    data_res = new_job.upload_data(sample_file, data_type='csv')
    assert data_res.status_code == 200

    if config.get('launch'):
        res = new_job.launch_job()

    return new_job.job_id


def contributor_submit_judgments(env,job_link, customer_name, customer_password):
    generate_judgments_for_job(env,job_link, customer_name, customer_password, all_units=False)

def main(user, password, api_key, env):
    config["user_name"] = user
    config["user_password"] = password
    job_id = create_job_from_config_api(config, 'fed', api_key, env_fed=env)
    job_link = generate_job_link_fed(job_id, api_key, env)
    contributor_submit_judgments(env, job_link, user, password)


if __name__ == "__main__":
    ENV = input("env: ")
    USER_NAME = input("username: ")
    PASSWORD = input("password: ")
    API_KEY = input("api key: ")

    main(USER_NAME, PASSWORD, API_KEY, ENV)
