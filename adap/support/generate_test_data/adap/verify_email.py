import datetime
import requests
import json

from adap.api_automation.utils.http_util import HttpMethod

base_url = "https://id.internal.{env}.cf3.us"

user_id = "/user_emails/{email}/user"
verify = "/users/{id}"


def find_user_id(email, env, api_key):
    service = HttpMethod()
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Token {api_key}',
        'Akon-Authentication-Token': f'{api_key}'
    }

    response = service.get(base_url.format(env=env)+user_id.format(email=email), headers=headers)
    print("-=-=",response)
    return response.json_response['id']


def update_email_verified(id, env, api_key):
    service = HttpMethod()
    today = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    payload = json.dumps({
        "user": {
            "email_verified_at": today
        }
    })

    headers = {
        'Authorization': f'Token {api_key}',
        'Content-Type': 'application/json',
        'Akon-Authentication-Token': api_key
    }

    response = service.put(base_url.format(env=env)+verify.format(id=id),
                           headers=headers,
                           data=payload)

    print("verification", response.json_response)


def verify_user_email_akon(email, env, api_key):
    user_id = find_user_id(email, env, api_key)
    update_email_verified(user_id, env, api_key)

# e.g
# api_key = '' - api key for cf_internal
# verify_user_email_akon('qa+new_test1@figure-eight.com', 'sandbox', '')