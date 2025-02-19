HEALTHCHECK = '/healthcheck'
CHECK_IP = '/ipqs/check/{ip}'


def URL(env):
    return {
        'qa': '',
        'stage': 'https://maas-ts-ip-quality-stage.appen.io'
    }.get(env)