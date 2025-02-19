CREATE_CHANNEL = '/hosted_channels?key={api_key}'
CONTRIBUTOR = '/hosted_channels/{hostedChannelId}/contributors?key={api_key}'
UPLOAD_CONTRIBUTORS = '/hosted_channels/contributors/metadata?key={api_key}'
DOWNLOAD_CONTRIBUTORS = '/hosted_channels/{hostedChannelId}/contributors/export?key={api_key}'
UPDATE_METADATA = '/hosted_channels/contributors/{email}/metadata?key={api_key}'
DELETE_CHANNEL = '/hosted_channels/{hostedChannelId}?key={api_key}'
DELETE_LIST_CONTRIBUTORS = '/hosted_channels/{hostedChannelId}/contributors/remove?key={api_key}'
UPDATE_CHANNEL_NAME = '/hosted_channels/{hostedChannelId}?key={api_key}'

URL = "https://api-proxy.{}.cf3.us/v1"
FED = "https://app.{}.secure.cf3.us/api-proxy/v1"
FED_CUSTOMIZE = "https://{}/api-proxy/v1"

