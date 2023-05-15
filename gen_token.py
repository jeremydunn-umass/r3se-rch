from __future__ import print_function

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

#Modfied version of the google quickstart.py https://github.com/googleworkspace/python-samples/blob/main/drive/quickstart/quickstart.py
# The generated token is hardcoded into the implant client and used to perform the API call to directly upload into the specified folder.
#The initial authentication done with this file has a popup that requires you to sign in and verify, once this is done we can use the provided
#json to upload without need for additional verification.
#
SCOPES = ['https://www.googleapis.com/auth/drive']


def main():
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """
    creds = None
    flow = InstalledAppFlow.from_client_secrets_file(
        'credentials.json', SCOPES)
    creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
    with open('token.json', 'w') as token:
        token.write(creds.to_json())

    try:
        service = build('drive', 'v3', credentials=creds)
    except HttpError as error:
        print(f'An error occurred: {error}')


if __name__ == '__main__':
    main()
