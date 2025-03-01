URL = 'https://customer-data-service.internal.{env}.cf3.us/api/v1'

PROXY = '/proxy?team_id={team_id}&path={path}'
LINK = '/link?team_id={team_id}&path={path}'
REQUEST_TOKEN = '/request_token?team_id={team_id}&path={path}&expires_in={expires_in}'
REDEEM_TOKEN = '/redeem_token?{token}'
MANAGED_BUCKETS = '/managed_buckets'
TEAM_MANAGED_BUCKETS = '/managed_buckets/{team_id}'
GENERATE_URL = '/generate_url'
REDIRECT = '/redirect'
STORAGE_PROVIDERS = '/storage_providers'
STORAGE_PROVIDER_STATUS = '/storage_providers/{sp_id}/status'
