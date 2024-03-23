from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os.path
import pickle

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

creds = None
# The file token.pickle stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
if os.path.exists('token.pickle'):
    with open('token.pickle', 'rb') as token:
        creds = pickle.load(token)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentialsauth.json', SCOPES)
        creds = flow.run_local_server(port=52911)
    # Save the credentials for the next run
    with open('token.pickle', 'wb') as token:
        pickle.dump(creds, token)

# Build the Drive API service
service = build('drive', 'v3', credentials=creds)

def list_files(folder_id=None, indent=0):
    if folder_id:
        query = "'{}' in parents and visibility='anyoneWithLink'".format(folder_id)
    else:
        query = "trashed=false and visibility='anyoneWithLink'"

    results = service.files().list(
        q=query,
        fields="nextPageToken, files(id, name, mimeType)",
    ).execute()
    items = results.get('files', [])
    
    file_ids = []
    folder_ids = []

    for item in items:
        if item['mimeType'] == 'application/vnd.google-apps.folder':
            folder_ids.append(item['id'])
        else:
            file_ids.append(item['id'])

        if item['mimeType'] == 'application/vnd.google-apps.folder':
            list_files(item['id'], indent + 1)

    return file_ids, folder_ids