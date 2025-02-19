# """
# API tests for internal services, re https://appen.atlassian.net/browse/DO-9152
# """
#
import requests

ENV = 'integration'

# make user
team_id = '3cbb1002-a006-4ddd-a1e4-e1aa357bd8eb'
job_id = 1364210

# contributor
akon_id = ''
api_key = ''

if __name__ == '__main__':
    print("Contributor Statistics Service")
    header = {
        "Content-Type": "application/json",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "Accept": "application/json"
    }

    HOST = "https://contributor-analytics.internal." + ENV + ".cf3.us"
    URL = f'{HOST}/contributors/stats'
    resp = requests.get(URL, headers=header)
    assert len(resp.json()['data']) > 0
    assert resp.json()['errors'] is None


    print("ChannelService")
    header = {
                "Content-Type": "application/json",
                "Cache-Control": "no-cache",
                "Pragma": "no-cache"
            }
    HOST = "https://contributor-profiles.internal." + ENV + ".cf3.us"
    URL = f'{HOST}/v1/profiles/2122224/channel_workers'
    resp = requests.get(URL, headers=header)
    assert resp.status_code == 200
    assert len(resp.json()) > 0


    print("ContributoProfile")
    HOST = "https://contributor-profiles.internal." + ENV + ".cf3.us"
    URL = f"{HOST}/v1/profiles?search_type=akon_id&search_key={akon_id}"
    token = "Token " + api_key
    header = {
        "Content-Type": "application/json",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "Authorization": token
    }
    resp = requests.get(URL, headers=header)
    assert resp.status_code == 200
    assert resp.json().get('profile').get('id')


    print("Job-API")
    header = {
                "Content-Type": "application/json",
                "Cache-Control": "no-cache",
                "Pragma": "no-cache"
            }

    HOST = "https://jobs-api.internal." + ENV + ".cf3.us"
    URL = f"{HOST}/v1/jobs/{job_id}/channels"
    resp = requests.get(URL, headers=header)
    assert resp.status_code == 200
    assert 'vcare' in resp.json()

    URL = f"{HOST}/v1/jobs/{job_id}/validate?job_id={job_id}"
    resp = requests.get(URL, headers=header)
    assert resp.status_code == 204


    print("Tags")
    HOST = "https://tags.internal." + ENV + ".cf3.us"
    URL = f"{HOST}/v1/tag_associations"
    payload = {
        "resource_type": "job",
        "resource_id": job_id,
        "tag_ids": [
            25
        ]
    }
    resp = requests.post(URL, json=payload)
    assert resp.status_code == 200
    assert 'Test channel 2' in resp.text

    URL = f"{HOST}/v1/tag_associations?resource_type=job&resource_id={job_id}"
    resp = requests.get(URL)
    assert resp.status_code == 200
    assert 'Test channel 2' in resp.text

    URL = f"{HOST}/v1/tag_associations"
    resp = requests.delete(URL, json=payload)
    assert resp.status_code == 204

    URL = f"{HOST}/v1/tag_associations?resource_type=job&resource_id={job_id}"
    resp = requests.get(URL)
    assert resp.status_code == 200
    assert 'Test channel 2' not in resp.text


    print("CostReportingService")
    HOST = "https://cost-reporting.internal." + ENV + ".cf3.us"
    URL = f"{HOST}/v1/monthly_job_costs?team_id={team_id}&start_month=03/2020&end_month=04/2020"
    resp = requests.get(URL)
    assert resp.status_code == 200
    assert 'totals' in resp.json()


    print('ClientActionsAuditService')
    header = {
                "Content-Type": "application/json",
                "Cache-Control": "no-cache",
                "Pragma": "no-cache",
                "Accept": '*/*'
            }

    HOST = "https://caas.internal." + ENV + ".cf3.us"
    URL = f"{HOST}/v1/events.json?team_id={team_id}"
    resp = requests.get(URL, headers=header)
    assert resp.status_code == 200
    assert 'qa+performance1+user1@figure-eight.com' in resp.text


    print('NotificationsService')
    header = {
                "Content-Type": "application/json",
                "Cache-Control": "no-cache",
                "Pragma": "no-cache",
                "Accept": '*/*'
            }
    HOST = "https://notification.internal." + ENV + ".cf3.us"
    URL = f"{HOST}/v1/notices.json?team_id={team_id}"
    resp = requests.get(URL, headers=header)

    URL = f"{HOST}/v1/notice_definitions.json?category=requestor"
    resp = requests.get(URL, headers=header)
    assert resp.status_code == 200
    assert len(resp.json()) > 1

    URL = f"{HOST}/v1/notices.json?notice_id=24"
    resp = requests.get(URL, headers=header)
    assert resp.status_code == 200
    assert len(resp.json()) > 1