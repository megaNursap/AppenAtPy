
def URL(env):
    return {
        'qa': 'https://identity-service-qa.sandbox.cf3.us',
        'stage': 'https://identity-stage.integration.cf3.us',
        'integration': 'https://identity-stage.integration.cf3.us'
    }.get(env)


AUTH = "/auth/realms/QRP/protocol/openid-connect/auth"
TOKEN = "/auth/realms/QRP/protocol/openid-connect/token"
AUTHENTICATE = "/auth/realms/QRP/login-actions/authenticate"

AUTHENTICATE_params = {
    'session_code': '',
    'execution': '',
    'client_id': '',
    'tab_id': ''
}
