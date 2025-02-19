from __future__ import print_function

import base64
import email
import pickle
import os.path
import time

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import logging
logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)

# If modifying these scopes, delete the file token_qa.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def connect_gmail(env):
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token_qa.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    abs_path = os.path.abspath(os.path.dirname(__file__))
    if os.path.exists(abs_path+'/token_%s.pickle'% env):
        with open(abs_path+'/token_%s.pickle'% env, 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(abs_path+
                '/credentials_%s.json' % env, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        # with open(abs_path+'/token_qa.pickle', 'wb') as token:
        #     pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)

    return service


def get_invite_link(address, env):

    service = connect_gmail(env)
    # Call the Gmail API
    response = service.users().messages().list(userId='me',
                                               labelIds='UNREAD', maxResults=10).execute()

    max_try = 20
    current_try = 0
    while response['resultSizeEstimate'] == 0 or max_try<current_try:
        response = service.users().messages().list(userId='me',
                                                   labelIds='UNREAD', maxResults=10).execute()
        current_try+=1
        time.sleep(5)

    if response['resultSizeEstimate'] == 0:
        raise ValueError('No new emails found')

    for em in response['messages'][::-1]:
        message = service.users().messages().get(userId='me', id=em['id'], format='full').execute()

        if message.get("payload").get("body").get("data"):
            email_content = base64.urlsafe_b64decode(message.get("payload").get("body").get("data").encode("ASCII")).decode( "utf-8")
            mime_msg = email.message_from_string(email_content)

            if address in mime_msg.get_payload():
                new_data = mime_msg.get_payload()

                from urlextract import URLExtract
                extractor = URLExtract()
                urls = extractor.find_urls(new_data)
                msg_labels = {
                    "addLabelIds": ["TRASH"],
                    "removeLabelIds": ["UNREAD"]}
                try:
                    message = service.users().messages().modify(userId='me', id=em['id'],
                                                                body=msg_labels).execute()
                except:
                    print("Not able to Delete email")
                return urls

    return []


