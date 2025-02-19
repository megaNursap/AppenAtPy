CHECK_WORKER_BY_ID = '/detection/check/{worker_id}'
CHECK_WORKER_IP = '/detection/check/{worker_id}/ip'
CHECK_WORKER_LIST = '/detection/check'
HEALTHCHECK = '/healthcheck'


def URL(env):
    return {
        'qa': '',
        'stage': 'https://gateway-connect-stage.integration.cf3.us/test-maas-md'
    }.get(env)