from __future__ import print_function

import os.path
import base64
import pickle
import google.auth
import pandas as pd

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.message import EmailMessage

# If modifying these scopes, delete the file token.json.
SCOPES = [
        'https://www.googleapis.com/auth/gmail.modify',
        'https://www.googleapis.com/auth/gmail.settings.basic'
    ]

def credentialSetup():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())            
    return creds

def draftGmail(creds, content = 'This is automated draft mail', recipient = 'test@test.dev', sender = 'test1@test1.dev', subject = 'Automated draft'):
    try:
        # create gmail api client
        service = build('gmail', 'v1', credentials=creds)

        message = EmailMessage()

        message.set_content(content)

        message['To'] = recipient
        message['From'] = sender
        message['Subject'] = subject

        # encoded message
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        create_message = {
            "message": {
                "raw": encoded_message
            }
        }
        # pylint: disable=E1101
        draft = service.users().drafts().create(userId='me', body=create_message).execute()

        print(F'Draft id: {draft["id"]}\nDraft message: {draft["message"]}')

    except HttpError as error:
        print(F'An error occurred: {error}')
        draft = None

    return draft

def readGmail(creds, amount = 0, label = 'INBOX'):
    try:
        # Call the Gmail API
        service = build('gmail', 'v1', credentials=creds)
        results = service.users().messages().list(userId='me', labelIds=[label]).execute()
        messages = results.get('messages', [])
        message_count = amount if amount > 0 else len(messages)
        if not messages:
            print('No messages found.')
        else:
            message_from = []
            message_to = []
            message_subj = []
            message_content = []
            for message in messages[:message_count]:
                msg = service.users().messages().get(userId='me', id=message['id']).execute()
                snippet = msg['snippet']
                data = msg['payload']['headers']
                for value in data: 
                    if(value['name']=="From"):
                        message_from.append(value['value']) 
                    if(value['name']=="To"):
                        message_to.append(value['value']) 
                    if(value['name']=="Subject"):
                        message_subj.append(value['value']) 
                message_content.append(snippet)
            df = {'subject': message_subj, 'from': message_from, 'to': message_to, 'content': message_content}
            return pd.DataFrame(df)
    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f'An error occurred: {error}')
