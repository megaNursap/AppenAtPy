from adap.perf_platform.utils.logging import get_logger
import requests

URL = "https://qa-portal.internal.cf3.us/"

ENDPOINT = "api/v1/update_issues_status"
HEADERS = {
    "Content-type": "application/json"
}

LOGGER = get_logger(__name__)


def update_jira_tickets_status():
    res = requests.get(URL + ENDPOINT,
                       headers=HEADERS)
    LOGGER.info(f"========== Portal: update jira tickets status ==========")
    LOGGER.info(res.status_code)
    LOGGER.info(res.json())


if __name__ == '__main__':
    update_jira_tickets_status()
