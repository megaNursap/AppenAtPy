"""
Create new contributor with HTTP requests and validate email via Akon DB
"""

from adap.api_automation.utils.http_util import HttpMethod
from adap.perf_platform.utils.db import DBUtils
from bs4 import BeautifulSoup

base_url = 'https://account.integration.cf3.us/users'

user_email = 'qa+performance+worker99+2@figure-eight.com'
user_password = ''

akon_conn_params = {
    'host': '',
    'port': '',
    'user': '',
    'dbname': '',
    'password': ''
}

header = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
    "Content-Type": "application/x-www-form-urlencoded",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Pragma": "no-cache"
}

service = HttpMethod(session=True)

sign_up = service.get(f'{base_url}/new', headers=header)
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
                    base_url,
                    allow_redirects=True,
                    headers=header,
                    data=signup_form_data
                    )

assert sign_up_commit.status_code == 200, f'Something went wrong: {sign_up_commit.text} '


sql_validate_email = """
UPDATE users SET email_verified_at = NOW() WHERE email = %(email)s
"""

if __name__ == '__main__':
    with DBUtils(**akon_conn_params) as db:
        db.execute(
            sql_validate_email,
            args={'email': user_email}
            )
