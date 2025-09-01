import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.auth.exceptions import RefreshError
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar']
TOKEN_PATH = 'token.json'
CREDS_PATH = os.path.join('internal',
    'client_secret_923056037784-85mpqif3512ra0s9qjusjtqfnmkpv7el'
    '.apps.googleusercontent.com.json')

def get_credentials():
    creds = None

    # 1) Load existing token.json if it exists
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    # 2) If there are no (valid) credentials, or they’ve expired...
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except RefreshError:
                # Refresh token is invalid — delete and re-auth
                print("Invalid refresh token; deleting and reauthorizing.")
                os.remove(TOKEN_PATH)
                creds = None

        # 3) If we still don’t have creds (first-run or after a failed refresh)…
        if not creds:
            flow = InstalledAppFlow.from_client_secrets_file(CREDS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)

        # 4) Save for next time
        with open(TOKEN_PATH, 'w') as token_file:
            token_file.write(creds.to_json())

    # 5) Build and return the Calendar service client
    return build('calendar', 'v3', credentials=creds, static_discovery=False)
