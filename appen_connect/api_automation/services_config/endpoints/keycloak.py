
TOKEN = "/token"
USER = "/userinfo"


def URL(env):
    return {
        'qa': 'https://identity-service-qa.sandbox.cf3.us/auth/realms/QRP/protocol/openid-connect',
        'stage': 'https://identity-stage.integration.cf3.us/auth/realms/QRP/protocol/openid-connect'
    }.get(env)

