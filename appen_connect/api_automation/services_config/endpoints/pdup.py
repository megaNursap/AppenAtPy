CHECK_WORKER = '/duplicates/check/worker/'
CHECK_WORKER_BY_ID = '/duplicates/check/worker/{worker_id}'
CHECK_ATTRIBUTE = '/duplicates/check/attribute/{worker_id}'
HEALTHCHECK = '/healthcheck'


def URL(env):
    return {
        'qa': '',
        'stage': 'https://gateway-connect-stage.integration.cf3.us/test-maas-pdup'
    }.get(env)