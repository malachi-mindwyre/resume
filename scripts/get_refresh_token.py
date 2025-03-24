import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive.file']

def main():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Look for client_secret.json file in the project root
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            client_secret_file = os.path.join(project_root, 'client_secret.json')
            
            if not os.path.exists(client_secret_file):
                print("Error: client_secret.json file not found in project root.")
                print("Please add your Google API credentials file to the project root.")
                return
            flow = InstalledAppFlow.from_client_secrets_file(client_secret_file, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    print("Refresh token generated successfully!")

if __name__ == '__main__':
    main()
