#!/usr/bin/env python3
"""
Google Drive Handler

This script handles Google Drive operations for the resume processing system:
1. Download a Google Sheet to CSV
2. Upload the generated resume PDF to a specified folder

Requires Google API authentication with proper permissions.
"""

import os
import io
import logging
import pandas as pd
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

# Configure logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

# Google API scope for reading and writing files
SCOPES = ['https://www.googleapis.com/auth/drive']

# Location for storing credentials
TOKEN_FILE = 'token.json'
CREDENTIALS_FILE = 'credentials.json'

def authenticate_google_drive():
    """
    Authenticate with Google Drive API
    Returns Google Drive service object if successful, None otherwise
    """
    creds = None

    # Check if token.json exists with stored credentials
    if os.path.exists(TOKEN_FILE):
        try:
            creds = Credentials.from_authorized_user_info(TOKEN_FILE, SCOPES)
        except Exception as e:
            logger.warning(f"Error loading stored credentials: {e}")
    
    # If credentials don't exist or are invalid, go through OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                logger.warning(f"Error refreshing credentials: {e}")
                creds = None
        
        if not creds:
            # Check if credentials file exists
            if not os.path.exists(CREDENTIALS_FILE):
                logger.error(f"Credentials file '{CREDENTIALS_FILE}' not found. Please download it from Google Cloud Console.")
                logger.info("Instructions: \n"
                          "1. Go to https://console.cloud.google.com/\n"
                          "2. Create a new project\n"
                          "3. Enable the Google Drive API\n"
                          "4. Create OAuth credentials (Desktop application)\n"
                          "5. Download the credentials and save as 'credentials.json'")
                return None
            
            # Start OAuth flow
            try:
                flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
                creds = flow.run_local_server(port=0)
                
                # Save credentials for next run
                with open(TOKEN_FILE, 'w') as token:
                    token.write(creds.to_json())
                logger.info("Google Drive authentication successful.")
            except Exception as e:
                logger.error(f"Error during authentication: {e}")
                return None
    
    # Build and return the Drive service
    try:
        service = build('drive', 'v3', credentials=creds)
        return service
    except Exception as e:
        logger.error(f"Error building Drive service: {e}")
        return None

def download_spreadsheet(spreadsheet_id, output_file):
    """
    Download a Google Sheet as CSV file
    
    Args:
        spreadsheet_id: ID of the Google Sheet (from URL)
        output_file: Path to save the downloaded CSV
    
    Returns:
        bool: True if successful, False otherwise
    """
    logger.info(f"Downloading Google Sheet {spreadsheet_id} to {output_file}")
    
    try:
        # Authenticate with Google Drive
        service = authenticate_google_drive()
        if not service:
            return False
        
        # Export Google Sheet as CSV
        request = service.files().export_media(
            fileId=spreadsheet_id,
            mimeType='text/csv'
        )
        
        # Stream the file content
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        
        while not done:
            status, done = downloader.next_chunk()
            logger.info(f"Download progress: {int(status.progress() * 100)}%")
        
        # Save the file
        fh.seek(0)
        csv_content = fh.read().decode('utf-8')
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Write to file
        with open(output_file, 'w') as f:
            f.write(csv_content)
        
        logger.info(f"Successfully downloaded Google Sheet to {output_file}")
        return True
    
    except Exception as e:
        logger.error(f"Error downloading Google Sheet: {e}")
        return False

def upload_pdf_to_drive(pdf_file, folder_id):
    """
    Upload a PDF file to a specific Google Drive folder
    
    Args:
        pdf_file: Path to the PDF file to upload
        folder_id: ID of the Google Drive folder (from URL)
    
    Returns:
        str: URL of the uploaded file if successful, None otherwise
    """
    logger.info(f"Uploading {pdf_file} to Google Drive folder {folder_id}")
    
    try:
        # Check if PDF file exists
        if not os.path.exists(pdf_file):
            logger.error(f"PDF file {pdf_file} not found")
            return None
        
        # Authenticate with Google Drive
        service = authenticate_google_drive()
        if not service:
            return None
        
        # Prepare file metadata
        file_metadata = {
            'name': os.path.basename(pdf_file),
            'parents': [folder_id]
        }
        
        # Prepare media
        media = MediaFileUpload(
            pdf_file,
            mimetype='application/pdf',
            resumable=True
        )
        
        # Upload file
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id,webViewLink'
        ).execute()
        
        # Get file ID and URL
        file_id = file.get('id')
        web_link = file.get('webViewLink')
        
        logger.info(f"Successfully uploaded {pdf_file} to Google Drive")
        logger.info(f"File ID: {file_id}")
        logger.info(f"Web link: {web_link}")
        
        return web_link
    
    except Exception as e:
        logger.error(f"Error uploading PDF to Google Drive: {e}")
        return None

if __name__ == "__main__":
    # Example usage
    import argparse
    
    parser = argparse.ArgumentParser(description='Google Drive operations for resume processing')
    parser.add_argument('--download', action='store_true', help='Download Google Sheet to CSV')
    parser.add_argument('--upload', action='store_true', help='Upload PDF to Google Drive')
    parser.add_argument('--sheet-id', default='1C20hzxMQzT310HSe9DhH8XigArW5VcjAGgQfGafF4o4', 
                        help='Google Sheet ID')
    parser.add_argument('--folder-id', default='1s6n9eS9d2NNy9lyXgoYdPGOwkyGGujnw', 
                        help='Google Drive folder ID')
    parser.add_argument('--csv-file', default='data/input/lead_gen.csv', help='Path for CSV file')
    parser.add_argument('--pdf-file', default='data/output/resume.pdf', help='Path for PDF file')
    
    args = parser.parse_args()
    
    if args.download:
        success = download_spreadsheet(args.sheet_id, args.csv_file)
        if success:
            print(f"✅ Successfully downloaded Google Sheet to {args.csv_file}")
        else:
            print(f"❌ Failed to download Google Sheet")
    
    if args.upload:
        url = upload_pdf_to_drive(args.pdf_file, args.folder_id)
        if url:
            print(f"✅ Successfully uploaded PDF to Google Drive")
            print(f"📎 Access your PDF at: {url}")
        else:
            print(f"❌ Failed to upload PDF to Google Drive")
