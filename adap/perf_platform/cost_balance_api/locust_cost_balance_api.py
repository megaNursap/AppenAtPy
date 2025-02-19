import json

from locust import between, TaskSequence, seq_task
from locust.exception import StopLocust

from adap.api_automation.utils.data_util import get_data_file
from adap.api_automation.utils.http_util import HttpMethod
from adap.api_automation.services_config.cost_balance_api_client import CostBalanceApiClient, clean_balance
from adap.perf_platform.utils.custom_locust import CustomLocust

from adap.perf_platform.utils.logging import get_logger
import random


log = get_logger(__name__, stdout=True)

base_url = "https://jobs-api.internal.integration.cf3.us"
api_team_balance = "/v1/team-balance/query"


path = get_data_file("/team_integration.json", "integration")
with open(path) as json_file:
    teams = json.load(json_file)


# https://appen.atlassian.net/browse/KEP-2072
class LocustUserBehavior(TaskSequence):
    def __init__(self, parent):
        super().__init__(parent)
        self.api_client = CostBalanceApiClient(HttpMethod(base_url))

    def on_start(self):
        self.team = random.choice(teams)
        teams.remove(self.team)

    def scenario_1(self):
        # INITIATE + CONFIRM DEDUCT Transaction
        team = self.team
        team_id = team.get('id')
        r_refund = self.api_client.initiate_refund_transaction(team_id, 10000)
        self.api_client.confirm_transaction(r_refund['uri'], r_refund['clientTransactionId'])

        for i in range(1000):
            r_deduct = self.api_client.initiate_deduct_transaction(team_id, 10)
            self.api_client.confirm_transaction(r_deduct['uri'], r_deduct['clientTransactionId'])

        # checks
        if self.api_client.get_teams_balance([team['id']])['teamBalancesResult'][0]['amountInCents'] != 0:
            log.error(f'Not zero team balance, - {team["id"]}')

    def scenario_2(self):
        # INITIATE + CONFIRM REFUND Transaction
        team = self.team
        team_id = team.get('id')

        for i in range(1000):
            r_refund = self.api_client.initiate_refund_transaction(team_id, 10)
            self.api_client.confirm_transaction(r_refund['uri'], r_refund['clientTransactionId'])

        # checks
        if self.api_client.get_teams_balance([team['id']])['teamBalancesResult'][0]['amountInCents'] != 10000:
            log.error(f'The team balance is not 10000, - {team["id"]}')

    def scenario_3(self):
        # INITIATE + CANCEL DEDUCT Balance
        team = self.team
        team_id = team.get('id')
        initial_balance = 10000
        r_refund = self.api_client.initiate_refund_transaction(team_id, initial_balance)
        self.api_client.confirm_transaction(r_refund['uri'], r_refund['clientTransactionId'])

        for i in range(1000):
            r_deduct = self.api_client.initiate_deduct_transaction(team_id, 10)
            self.api_client.cancel_transaction(r_deduct['uri'], r_deduct['clientTransactionId'])

        # checks
        if self.api_client.get_teams_balance([team['id']])['teamBalancesResult'][0]['amountInCents'] != initial_balance:
            log.error(f'The team balance is not {initial_balance}, - {team["id"]}')

    def scenario_4(self):
        # INITIATE + CANCEL REFUND Balance
        team = self.team
        team_id = team.get('id')

        for i in range(1000):
            r_refund = self.api_client.initiate_refund_transaction(team_id, 10)
            self.api_client.cancel_transaction(r_refund['uri'], r_refund['clientTransactionId'])

        # checks
        if self.api_client.get_teams_balance([team['id']])['teamBalancesResult'][0]['amountInCents'] != 0:
            log.error(f'Not zero team balance, - {team["id"]}')

    @seq_task(1)
    def cost_balance_perf_test(self):
        # specify needed scenario number (1-4)
        self.scenario_1()

    @seq_task(2)
    def done(self):
        raise StopLocust()


class LocustUser(CustomLocust):
    wait_time = between(0.001, 0.001)
    task_set = LocustUserBehavior
    host = base_url

    def __init__(self):
        super(LocustUser, self).__init__()

    def setup(self):
        clean_balance(base_url)

    def teardown(self):
        """ Locust teardown """
        log.info("Locust Teardown")
