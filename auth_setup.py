
import os
from google_auth_oauthlib.flow import InstalledAppFlow

# Define the scopes for the Blogger API
SCOPES = ['https://www.googleapis.com/auth/blogger']

def main():
    """
    This script handles the OAuth 2.0 flow to generate the `token.json` file
    required for authenticating with the Google Blogger API.
    """
    flow = InstalledAppFlow.from_client_secrets_file(
        'client_secret.json', SCOPES)
    creds = flow.run_local_server(port=0)

    # Save the credentials for the next run
    with open('token.json', 'w') as token:
        token.write(creds.to_json())
    print("Authentication successful. `token.json` created.")

if __name__ == '__main__':
    main()
