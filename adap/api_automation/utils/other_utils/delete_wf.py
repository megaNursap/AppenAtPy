import requests
from adap.api_automation.services_config.workflow import Workflow

url = "https://api-beta.sandbox.cf3.us/v2"
internal_url = "https://workflows-service.internal.sandbox.cf3.us/v1"
api_key = ""
user_id = "6337e02e-2957-4549-b554-8f5d47a929de"
payload = {
    "user_id": user_id,
    "limit": 3
}

wf = Workflow(api_key, custom_url=internal_url, env="sandbox")
res = wf.service.get('/workflows', params=payload)
print(res.json_response)


for current_wf in res.json_response['workflows']:
    print("-=-=-=-=-=-=-=-")

    if current_wf['status'] == 'running':
        res = wf.pause(current_wf['id'])
        print(res.status_code)
    elif current_wf['status'] != 'paused':
        wf.delete_wf(current_wf['id'])
        print(current_wf)

# res = wf.get_list_of_wfs()
# print(res.json_response)



