"""
Create new requestors with HTTP requests and validate email via Akon DB
"""

from adap.api_automation.utils.http_util import HttpMethod
from adap.perf_platform.utils.db import DBUtils
from bs4 import BeautifulSoup
import os

class Service:
    def __init__(self, env: str, akon_conn_params: dict, *args, **kwargs):
        self.base_url = f'https://client.{env}.cf3.us'
        # akon_conn_params = {
        #     'host': '',
        #     'port': '',
        #     'user': '',
        #     'dbname': '',
        #     'password': ''
        # }
        self.akon_conn_params = akon_conn_params
        self.builder_conn_params = kwargs.get('builder_conn_params')
        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
            "Content-Type": "application/x-www-form-urlencoded",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Pragma": "no-cache"
        }

    def signup(self, user_email, password):
        service = HttpMethod(session=True)
        sign_up = service.get(f'{self.base_url}/users/new', headers=self.headers)
        sign_up_soup = BeautifulSoup(sign_up.text, 'html.parser')
        authenticity_token = sign_up_soup.find('input', {'name': 'authenticity_token'}).get('value')
        signup_form_data = {
            "authenticity_token": authenticity_token,
            "user[name]": user_email,
            "user[email]": user_email,
            "user[password]": password,
            "user[password_confirmation]": password,
            "user[force_disposable_email_check]": 'false',
            "terms": 'on',
            "commit": 'Create My Free Account'
        }
        sign_up_commit = service.post(
                            f'{self.base_url}/users',
                            allow_redirects=True,
                            headers=self.headers,
                            data=signup_form_data
                            )
        assert sign_up_commit.status_code == 200, f'Something went wrong: {sign_up_commit.text} '


    def verify_email(self, user_email):
        sql_validate_email = """
        UPDATE users SET email_verified_at = NOW() WHERE email = %(email)s
        """
        with DBUtils(**self.akon_conn_params) as db:
            db.execute(
                sql_validate_email,
                args={'email': user_email}
                )
    
    def get_user_team_id(self, user_email):
        with DBUtils(**self.akon_conn_params) as db:
            team_id = db.fetch_one(
                "select api_team_id from users WHERE email = %(email)s",
                args={'email': user_email}
                )[0]
        return team_id

    def make_cf_internal(self, user_email):
        team_id = self.get_user_team_id(user_email)
        with DBUtils(**self.akon_conn_params) as db:
            db.execute(
                """
                delete from roles_teams where team_id = %(team_id)s;
                insert into roles_teams (role_id, team_id) values (4, %(team_id)s);
                """,
                args={'team_id': team_id}
                )

    def add_funds(self, user_email, amount):
        team_id = self.get_user_team_id(user_email)
        assert self.builder_conn_params, "builder_conn_params is not set"
        with DBUtils(**self.builder_conn_params) as db:
            db.execute(
                """
                UPDATE credit_balances
                SET amount = %(amount)s, updated_at = NOW()
                WHERE team_id = %(team_id)s
                """,
                args={
                    'amount': amount,
                    'team_id': team_id
                }
            )

    def set_row_limit(self, user_email, amount):
        team_id = self.get_user_team_id(user_email)
        with DBUtils(**self.akon_conn_params) as db:
            db.execute(
                """
                UPDATE teams SET available_units = %(amount)s
                WHERE id = %(team_id)s
                """,
                args={
                    'amount': amount,
                    'team_id': team_id
                }
            )

    def set_available_rows(self, user_email, amount):
        team_id = self.get_user_team_id(user_email)
        with DBUtils(**self.akon_conn_params) as db:
            db.execute(
                """
                UPDATE subscriptions SET number_units = %(amount)s
                WHERE team_id = %(team_id)s
                """,
                args={
                    'amount': amount,
                    'team_id': team_id
                }
            )


if __name__ == '__main__':

    akon_conn_params = {
        'host': os.environ.get('AKON_DB_HOST'),
        'port': os.environ.get('AKON_DB_PORT'),
        'dbname': os.environ.get('AKON_DB_NAME'),
        'user': os.environ.get('AKON_DB_USER'),
        'password': os.environ.get('AKON_DB_PASSWORD')
    }
    service = Service('integration', akon_conn_params)

    user_template = 'qa+performance2+user{_id}@figure-eight.com'
    users = [user_template.format(_id=i) for i in range(100)]
    user_password = 'Test123!'

    for user_email in users:
        service.signup(user_email, user_password)
        service.verify_email(user_email)
        service.make_cf_internal(user_email)
