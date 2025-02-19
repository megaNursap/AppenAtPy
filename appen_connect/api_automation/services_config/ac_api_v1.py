import json

import allure
import pytest

from appen_connect.api_automation.services_config.endpoints.ac_api_v1 import *

from adap.api_automation.utils.http_util import HttpMethod


class AC_API_V1:

    def __init__(self, auth_key, custom_url=None, payload=None, headers=None, env=None):
        self.payload = payload
        self.auth_key = auth_key

        if env is None and custom_url is None:  env = pytest.env
        self.env = env

        if custom_url is not None:
            self.url = custom_url
        else:
            self.url = URL(env=pytest.env)

        if not headers:
            self.headers = {
                'accept': 'application/json'
            }

        self.service = HttpMethod(self.url, self.payload)

    @allure.step
    def send_email(self, payload=None):
        headers = {
            'Content-Type': 'application/json',
            'X-UNITY-ApiAuth': self.auth_key
        }
        res = self.service.post(EMAIL, headers=headers, data=json.dumps(payload))
        return res

    @allure.step
    def get_project(self, project_id):
        headers = {
            'Content-Type': 'application/json',
            'X-UNITY-ApiAuth': self.auth_key
        }
        res = self.service.get(PROJECT.format(id=project_id), headers=headers)

        return res

    @allure.step
    def get_project_ias(self, project_id):
        headers = {
            'Content-Type': 'application/json',
            'X-UNITY-ApiAuth': self.auth_key
        }
        res = self.service.get(PROJECT_IAS.format(id=project_id), headers=headers)
        return res

    @allure.step
    def get_project_guidelines(self, project_id):
        headers = {
            'Content-Type': 'application/json',
            'X-UNITY-ApiAuth': self.auth_key
        }
        res = self.service.get(PROJECT_GUIDELINES.format(projectId=project_id), headers=headers)
        return res

    @allure.step
    def get_user_guidelines(self, user_id):
        headers = {
            'Content-Type': 'application/json',
            'X-UNITY-ApiAuth': self.auth_key
        }
        res = self.service.get(USER_GUIDELINES.format(userId=user_id), headers=headers)
        return res

    @allure.step
    def get_user_guideline_document(self, user_id, document_id):
        headers = {
            'Content-Type': 'application/json',
            'X-UNITY-ApiAuth': self.auth_key
        }
        res = self.service.get(GUIDLINE_DOCUMENT.format(userId=user_id, documentId=document_id), headers=headers)
        return res

    @allure.step
    def post_guideline_acknowledgement(self, payload=None):
        headers = {
            'Content-Type': 'application/json',
            'X-UNITY-ApiAuth': self.auth_key
        }
        res = self.service.post(GUIDELINES, headers=headers, data=json.dumps(payload))
        return res

    @allure.step
    def get_invoice(self, invoice_id):
        headers = {
            'Content-Type': 'application/json',
            'X-UNITY-ApiAuth': self.auth_key
        }
        res = self.service.get(GET_INVOICE.format(id=invoice_id), headers=headers)
        return res

    @allure.step
    def get_customer_attributes(self, customer_id):
        headers = {
            'Content-Type': 'application/json',
            'X-UNITY-ApiAuth': self.auth_key
        }
        res = self.service.get(CUSTOMER.format(id=customer_id), headers=headers)
        return res

    @allure.step
    def find_invoice(self, params=None):
        headers = {
            'Content-Type': 'application/json',
            'X-UNITY-ApiAuth': self.auth_key
        }
        res = self.service.get(FIND_INVOICE, headers=headers, params=params)
        return res

    @allure.step
    def get_user_by_email(self, payload):
        headers = {
            'Content-Type': 'application/json',
            'X-UNITY-ApiAuth': self.auth_key
        }
        res = self.service.get(USERS, headers=headers, params=payload)
        return res

    @allure.step
    def get_user_by_id(self, user_id, payload=None):
        headers = {
            'Content-Type': 'application/json',
            'X-UNITY-ApiAuth': self.auth_key
        }
        res = self.service.get(USER.format(id=user_id), headers=headers, params=payload)
        return res

    @allure.step
    def get_users_for_project(self, project_id, payload=None):
        headers = {
            'Content-Type': 'application/json',
            'X-UNITY-ApiAuth': self.auth_key
        }
        self.payload = payload
        res = self.service.get(USERS_PROJECT.format(projectId=project_id), headers=headers, params=self.payload)
        return res

    @allure.step
    def create_invoice(self, payload=None):
        headers = {
            'Content-Type': 'application/json',
            'X-UNITY-ApiAuth': self.auth_key
        }
        res = self.service.post(CREATE_INVOICE, headers=headers, data=json.dumps(payload))
        return res

    @allure.step
    def find_invoices(self, payload=None):
        headers = {
            'Content-Type': 'application/json',
            'X-UNITY-ApiAuth': self.auth_key
        }
        res = self.service.put(FIND_INVOICES, headers=headers, data=json.dumps(payload))
        return res

    @allure.step
    def get_intelligent_attribute(self, payload=None):
        headers = {
            'Content-Type': 'application/json',
            'X-UNITY-ApiAuth': self.auth_key
        }
        res = self.service.get(INTELLIGENT_ATTRIBUTE, headers=headers, params=payload)
        return res

    @allure.step
    def create_invoices(self, payload=None):
        headers = {
            'Content-Type': 'application/json',
            'X-UNITY-ApiAuth': self.auth_key
        }
        res = self.service.post(CREATE_INVOICES, headers=headers, data=json.dumps(payload))
        return res

    @allure.step
    def create_partner_data(self, payload=None):
        headers = {
            'Content-Type': 'application/json',
            'X-UNITY-ApiAuth': self.auth_key
        }
        res = self.service.post(PARTNER_DATA_API, headers=headers, data=json.dumps(payload))
        return res

    @allure.step
    def check_user_password(self, user, password=None):
        headers = {
            'Content-Type': 'application/json;charset=UTF-8',
            'X-UNITY-ApiAuth': self.auth_key,
            'Accept': 'application/json;charset=UTF-8'
        }

        res = self.service.put(CHECK_PASSWORD + "?email={}".format(user), headers=headers, data=password)
        return res

    @allure.step
    def post_faceid_for_user(self, user, faceid):
        headers = {
            'Content-Type': 'application/json',
            'X-UNITY-ApiAuth': self.auth_key
        }
        res = self.service.post(FACE_ID.format(userId=user) + "?faceId={}".format(faceid), headers=headers)
        return res

    @allure.step
    def post_opt_in_acknowledge(self, payload=None):
        headers = {
            'Content-Type': 'application/json',
            'X-UNITY-ApiAuth': self.auth_key
        }
        res = self.service.post(OPT_IN_ACKNOWLEDGE + "?a9-ack={}".format(payload), headers=headers)
        return res

    @allure.step
    def user_token_validation_api(self, tenantId, userId, data):
        headers = {
            'Content-Type': 'application/json',
            'X-UNITY-ApiAuth': self.auth_key,
            'Accept': 'application/json;charset=UTF-8'
        }
        res = self.service.put(SWS_USER_TOKEN_VALIDATION_API + "?tenantId={}&userId={}".format(tenantId, userId),
                               data=data, headers=headers)
        return res

    @allure.step
    def get_approve_user(self, payeeid, programid):
        headers = {
            'Content-Type': 'application/json',
            'X-UNITY-ApiAuth': self.auth_key,
            'Accept': 'application/json;charset=UTF-8'
        }
        res = self.service.get(GET_APPROVE_USER + "?payeeid={}&programid={}".format(payeeid, programid), headers=headers)
        return res

    @allure.step
    def get_decline_user(self, payeeid, programid):
        headers = {
            'Content-Type': 'application/json',
            'X-UNITY-ApiAuth': self.auth_key,
            'Accept': 'application/json;charset=UTF-8'
        }
        res = self.service.get(GET_DECLINE_USER + "?payeeid={}&programid={}".format(payeeid, programid), headers=headers)
        return res

    @allure.step
    def get_payoneer_registration(self, payeeid, programid, payoneerid=None):
        headers = {
            'Content-Type': 'application/json',
            'X-UNITY-ApiAuth': self.auth_key,
            'Accept': 'application/json;charset=UTF-8'
        }
        res = self.service.get(
            GET_PAYONEER_REGISTRATION + "?payeeid={}&programid={}&payoneerID={}".format(payeeid, programid, payoneerid),
            headers=headers)
        return res

    @allure.step
    def get_cancel_payment(self, client_reference_id, payment_amount, reason_code, reason_description, payee_id):
        headers = {
            'Content-Type': 'application/json',
            'X-UNITY-ApiAuth': self.auth_key,
            'Accept': 'application/json;charset=UTF-8'
        }
        res = self.service.get(GET_PAYONEER_REGISTRATION + "?ClientReferenceId={}&PaymentAmount={}&ReasonCode={"
                                                           "}&ReasonDescription={}&payeeId={}".format(
            client_reference_id, payment_amount, reason_code, reason_description, payee_id, headers=headers))
        return res

    @allure.step
    def get_payrate(self, businessUnit, rateType):
        headers = {
            'Content-Type': 'application/json',
            'X-UNITY-ApiAuth': self.auth_key,
            'Accept': 'application/json;charset=UTF-8'
        }
        res = self.service.get(GET_PAYRATE.format(businessUnit=businessUnit) + "?rateType={}".format(rateType),
                               headers=headers)
        return res

    @allure.step
    def get_ticket_prepare_response(self, ticketId):
        headers = {
            'Content-Type': 'application/json',
            'X-UNITY-ApiAuth': self.auth_key
        }
        res = self.service.get(TICKETS_PREPARE_RESPONSE + "?ticketId={}".format(ticketId), headers=headers)
        return res

    @allure.step
    def get_smart_ticket_answering_by_id(self, ticketId):
        headers = {
            'Content-Type': 'application/json',
            'X-UNITY-ApiAuth': self.auth_key
        }
        res = self.service.get(SMART_TICKET_ANSWERING_BY_ID + "?ticketId={}".format(ticketId), headers=headers)
        return res

    @allure.step
    def post_smart_ticket_answering(self, payload=None):
        headers = {
            'Content-Type': 'application/json',
            'X-UNITY-ApiAuth': self.auth_key
        }
        res = self.service.post(SMART_TICKET_ANSWERING, headers=headers, data=json.dumps(payload))
        return res
