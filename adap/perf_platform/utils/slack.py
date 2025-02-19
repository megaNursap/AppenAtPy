import requests
import json
from adap.settings import Config
from adap.perf_platform.utils.logging import get_logger

log = get_logger(__name__)
chat_post_message_url = "https://slack.com/api/chat.postMessage"
chat_update_url = "https://slack.com/api/chat.update"
headers = {
        'Content-type': 'application/json',
        'Authorization': f'Bearer {Config.SLACK_TOKEN}'
    }
text_template = "*[{env}] Platform Performance Test Results*\n{message}"


def post_performance_results(text: str, thread_ts=None):
    data = {
        'as_user': 'false',
        'channel': Config.SLACK_CHANNEL,
        # "attachments": [{
        #   "text": text,
        #   "title": f"[{Config.ENV}] Platform Load Test",
        #   "color": "#0099FF"
        # }]
        "blocks": [
            {
              "type": "section",
              "text": {
                "type": "mrkdwn",
                "text": text
                }
            },
            # {
            #   "type": "divider"
            # },
        ],
    }
    if thread_ts is not None:
        data['thread_ts'] = thread_ts
    data_json = json.dumps(data)
    log.debug(data_json)
    resp = requests.post(
        chat_post_message_url,
        headers=headers,
        data=data_json)
    error_message = f"{resp.status_code}, {resp.text}"
    assert resp.status_code == 200, error_message
    assert resp.json().get('ok'), error_message
    log.debug(resp.text)
    return resp


def update_message(text: str, ts: str, channel: str):
    data = {
        'as_user': 'false',
        'channel': channel,
        'ts': ts,
        'blocks': [
            {
              "type": "section",
              "text": {
                "type": "mrkdwn",
                "text": text
                }
            },
        ],
    }
    data_json = json.dumps(data)
    log.debug(data_json)
    resp = requests.post(
        chat_update_url,
        headers=headers,
        data=data_json)
    error_message = f"{resp.status_code}, {resp.text}"
    assert resp.status_code == 200, error_message
    assert resp.json().get('ok'), error_message
    log.debug(resp.text)
    return resp


def upload_snippet(content, channel, thread_ts=None, initial_comment=None):
    url = 'https://slack.com/api/files.upload'
    data = {
        'channels': channel,
        'content': content,
        'initial_comment': initial_comment
    }
    if thread_ts is not None:
        data['thread_ts'] = thread_ts
    data_json = json.dumps(data)
    log.debug(data_json)
    resp = requests.post(
        url,
        headers=headers,
        data=data_json)
    error_message = f"{resp.status_code}, {resp.text}"
    assert resp.status_code == 200, error_message
    assert resp.json().get('ok'), error_message
    log.debug(resp.text)
    return resp
