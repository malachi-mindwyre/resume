# Google Drive Integration Setup Guide

This guide explains how to set up Google Drive integration for the resume processing tool.

## Prerequisites

1. Google account
2. Basic understanding of the Google Cloud Console

## Step 1: Create a Google Cloud Project

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Create Project" or select an existing project
3. Give your project a name (e.g., "Resume Keywords Tool")
4. Click "Create"

## Step 2: Enable the Google Drive API

1. In your Google Cloud project, go to "APIs & Services" > "Library"
2. Search for "Google Drive API"
3. Click on "Google Drive API" from the results
4. Click "Enable"

## Step 3: Configure OAuth Consent Screen

1. Go to "APIs & Services" > "OAuth consent screen"
2. Select "External" user type (unless you have a Google Workspace account)
3. Click "Create"
4. Fill in the required information:
   - App name: "Resume Keywords Tool"
   - User support email: your email address
   - Developer contact information: your email address
5. Click "Save and Continue"
6. On the "Scopes" screen, click "Add or Remove Scopes"
7. Add the following scope: `https://www.googleapis.com/auth/drive`
8. Click "Save and Continue"
9. Add yourself as a test user and click "Save and Continue"
10. Review your settings and click "Back to Dashboard"

## Step 4: Create OAuth 2.0 Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. For Application type, select "Desktop application"
4. Name your client (e.g., "Resume Keywords Desktop Client")
5. Click "Create"
6. A pop-up will show your client ID and client secret - click "Download JSON"
7. Rename the downloaded file to `credentials.json` and move it to the project root directory

## Step 5: Test the Integration

1. Run the script with Google Drive integration:
   ```bash
   python3 scripts/easy_resume_processor_with_drive.py
   ```
2. The first time you run it, a browser window will open asking you to authorize the application
3. Sign in with your Google account and grant the requested permissions
4. The script will then proceed to download data from your Google Sheet and later upload the PDF

## Troubleshooting

### Authentication Issues

- If you see "This app is not verified" warning, click "Advanced" and then "Go to (app name) (unsafe)"
- If authentication fails, delete the `token.json` file (if it exists) and try again
- Ensure you've enabled the correct API and have the right scopes in your OAuth consent screen

### Sheet Access Issues

- Make sure your Google Sheet is shared with the Google account you're authenticating with
- Verify the Sheet ID is correct (it's the long string of characters in the Sheet URL)
- The Google Sheet must have columns named `high_priority_keywords` and `low_priority_keywords`

### Upload Issues

- Make sure your Google Drive folder is accessible to your Google account
- Verify the folder ID is correct (it's the string of characters in the folder URL)
- Check that the PDF file was successfully generated before attempting to upload

## Google Sheet Format

Your Google Sheet should have the following structure:

| high_priority_keywords | low_priority_keywords |
|------------------------|----------------------|
| Python                 | interpersonal skills |
| SQL                    | communication        |
| data visualization     | team player          |
| ...                    | ...                  |

Where:
- `high_priority_keywords`: Keywords that are most important for your resume
- `low_priority_keywords`: Secondary keywords that are still beneficial but less critical