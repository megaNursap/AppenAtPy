"""
Create new contributors on ADAP using HTTP requests and validate email via Akon DB
Running concurrently with gevent

Usage:
1. Provide BASE_URL for ADAP annotation site (for Integration it's "https://account.integration.cf3.us/users")
2. Provide USER_PASSWORD (common for all users)
3. Provide Akon DB credentials (akon_db_conn_params) - credentials can be found in LastPass as `preprod DB URIs`
4. Run the script as `python scripts/one_offs/create_contributors_api.py`

Example :
params = [
    {'user_email':testing1@example.com, 'user_password': 'Testing123!'},
    {'user_email':testing2@example.com, 'user_password': 'Testing123!'},
    {'user_email':testing3@example.com, 'user_password': 'Testing123!'},
]
execute_concurrently(sign_up, params, concurrency=CONCURRENCY)
"""

from adap.api_automation.utils.http_util import HttpMethod
from adap.perf_platform.utils.db import DBUtils
from bs4 import BeautifulSoup
import gevent
import math

from adap.perf_platform.test_data import integration_contributor_emails

BASE_URL = 'https://account.sandbox.cf3.us/users'
USER_PASSWORD = ''
CONCURRENCY = 10

akon_db_conn_params = {
    'host': '',
    'port': '',
    'user': '',
    'dbname': '',
    'password': ''
}


def execute_concurrently(func, params: list, concurrency: int):
    """
    Execute funcion `func` for each item in `params` using # of gevent threads
    set by `concurrency`. Each item in `params` is expected to be a dict
    containing kwargs passed to `func`
    """
    def gevent_worker(func, params: int):
        for p in params:
            func(**p)
    tasks = []
    step =  math.ceil(len(params)/concurrency)
    for c in range(1,concurrency+1):
        params_c = params[(c-1) * step : c * step]
        tasks.append(gevent.spawn(gevent_worker, func, params_c))
    gevent.joinall(tasks)


def validate_email(user_email):
    sql_validate_email = """
    UPDATE users SET email_verified_at = NOW() WHERE email = %(email)s
    """
    with DBUtils(**akon_db_conn_params) as db:
        db.execute(
            sql_validate_email,
            args={'email': user_email}
            )


def sign_up(user_email, user_password, BASE_URL, validate=True):
    header = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
        "Content-Type": "application/x-www-form-urlencoded",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Pragma": "no-cache"
    }
    service = HttpMethod(session=True)
    sign_up = service.get(f'{BASE_URL}/new', headers=header)
    sign_up_soup = BeautifulSoup(sign_up.text, 'html.parser')
    authenticity_token = sign_up_soup.find('input', {'name': 'authenticity_token'}).get('value')
    signup_form_data = {
        "authenticity_token": authenticity_token,
        "user[name]": user_email,
        "user[email]": user_email,
        "user[password]": user_password,
        "user[password_confirmation]": user_password,
        "user[force_disposable_email_check]": 'false',
        "terms": 'on',
        "commit": 'Create My Free Account'
    }
    sign_up_commit = service.post(
        BASE_URL,
        allow_redirects=True,
        headers=header,
        data=signup_form_data
    )
    assert sign_up_commit.status_code == 200, ''\
        f'Error: {sign_up_commit.text}'

    if validate:
       validate_email(user_email)
    

if __name__ == '__main__':
    # Create worker accounts from the integration_contributor_emails list
    worker_emails = integration_contributor_emails.get()

    params = []
    for e in worker_emails:
        params.append({'user_email': e['worker_email'], 'user_password': USER_PASSWORD})
    execute_concurrently(sign_up, params, concurrency=CONCURRENCY)
    

