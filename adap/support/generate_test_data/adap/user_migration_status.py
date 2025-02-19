import datetime
import requests
import json

from adap.api_automation.utils.http_util import HttpMethod

base_url = "https://feca.internal.integration.cf3.us/v1"

migration_status = "/admin/users/connect_migration_status"
user = "/admin/users/{id}"


def get_migration_user_id(email):
    service = HttpMethod()
    headers = {
        'Content-Type': 'application/json',
    }
    payload = json.dumps({"email": email})

    response = service.get(base_url+migration_status, headers=headers, data=payload)
    print("-=-=", response)
    return response.json_response['id']


def update_migration_status(user_id, status):
    service = HttpMethod()

    payload = json.dumps({
        "user": {
            "connect_migration_status": status
        }
    })

    headers = {
        'Content-Type': 'application/json',
    }

    response = service.put(base_url+user.format(id=user_id),
                           headers=headers,
                           data=payload)

    print("-=-=", response)
    return response.json_response
