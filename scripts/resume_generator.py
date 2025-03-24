#!/usr/bin/env python3
"""
Simple Resume Generator

This script provides a straightforward way to:
1. Process keywords from job descriptions
2. Apply them to a resume template
3. Format the resume and generate a PDF
4. Upload the PDF to Google Drive
"""

import pandas as pd
import os
import re
import subprocess
import yaml
import argparse
import shutil
import pickle
from collections import Counter
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload

# Default capitalization rules
SPECIAL_TERMS = {
    'aws': 'AWS',
    'aws cloud': 'AWS Cloud',
    'aws cloud devops': 'AWS Cloud DevOps',
    'python': 'Python',
    'sql': 'SQL',
    'r': 'R',
    'gcp': 'GCP',
    'etl': 'ETL',
}

# Google Drive folder ID where you want to save your resume
# Replace with your own folder ID
DRIVE_FOLDER_ID = '1s6n9eS9d2NNy9lyXgoYdPGOwkyGGujnw'

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive.file']

# Default YAML header for the resume
YAML_HEADER = """---
geometry: margin=0.5in
output: pdf_document
header-includes:
  - \\usepackage{fancyhdr}
  - \\pagestyle{empty}
  - \\pagenumbering{gobble}
  - \\usepackage{hyperref}
  - \\hypersetup{colorlinks=true, linkcolor=blue, urlcolor=blue}
---
"""

def process_keywords(input_file, output_file):
    """Process keywords from a job description file"""
    print(f"Processing keywords from {input_file}...")
    
    # Load CSV file
    df = pd.read_csv(input_file)
    
    # Function to extract keywords
    def extract_keywords(text):
        if pd.isnull(text):
            return []
        # Lower-case and remove punctuation
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        # Split on whitespace and handle multi-word phrases
        keywords = []
        for word in text.split():
            keywords.append(word)
        # Also add the original text as a potential multi-word phrase
        if not pd.isnull(text) and len(text.strip()) > 0:
            original_text = text.lower()
            original_text = re.sub(r'[^\w\s-]', ' ', original_text)
            # Add the entire phrase if it contains multiple words
            if len(original_text.split()) > 1:
                keywords.append(original_text)
        return keywords
    
    # Apply extraction to both columns
    df["high_keywords"] = df["high_priority_keywords"].apply(extract_keywords)
    df["low_keywords"] = df["low_priority_keywords"].apply(extract_keywords)
    
    # Count keywords
    high_counter = Counter()
    low_counter = Counter()
    
    for keywords in df["high_keywords"]:
        high_counter.update(keywords)
    for keywords in df["low_keywords"]:
        low_counter.update(keywords)
    
    # Convert to dataframes
    high_df = pd.DataFrame(high_counter.items(), columns=["keyword", "count"]).sort_values(by="count", ascending=False)
    low_df = pd.DataFrame(low_counter.items(), columns=["keyword", "count"]).sort_values(by="count", ascending=False)
    
    # Save to output CSV
    with open(output_file, 'w', newline='') as f:
        f.write("keyword,count,priority\n")
        
        # Write high priority keywords
        for _, row in high_df.iterrows():
            f.write(f"{row['keyword']},{row['count']},high\n")
            
        # Write low priority keywords
        for _, row in low_df.iterrows():
            f.write(f"{row['keyword']},{row['count']},low\n")
    
    print(f"Processed keywords saved to {output_file}")
    return high_df.head(20)["keyword"].tolist()

def fix_capitalization(content):
    """Fix capitalization of specific terms"""
    
    # For each special term, replace it with proper capitalization
    for term, capitalized in SPECIAL_TERMS.items():
        # Create pattern to match the term regardless of case
        pattern = r'\b' + re.escape(term) + r'\b'
        content = re.sub(pattern, capitalized, content, flags=re.IGNORECASE)
    
    # Fix ampersands for LaTeX
    content = content.replace(' & ', ' \\& ')
    
    return content

def load_resume_config(config_file):
    """Load resume configuration from YAML file"""
    try:
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        return config
    except Exception as e:
        print(f"Error loading configuration: {e}")
        return None

def find_unused_keywords(resume_content, keywords_file, min_count=2):
    """Find keywords from the processed file that aren't in the resume content"""
    try:
        df = pd.read_csv(keywords_file)
        
        # Filter keywords by count
        df = df[df['count'] >= min_count]
        
        # Convert resume content to lowercase for comparison
        resume_lower = resume_content.lower()
        
        # Find keywords not in resume
        unused_keywords = []
        for _, row in df.iterrows():
            keyword = row['keyword']
            # Skip one-letter keywords and keywords less than 3 characters
            if len(keyword) < 3:
                continue
            
            # Check if the keyword is not in the resume
            if keyword.lower() not in resume_lower:
                # Capitalize properly
                if keyword in SPECIAL_TERMS:
                    unused_keywords.append(SPECIAL_TERMS[keyword])
                elif keyword.lower() == keyword:
                    # Capitalize first letter of each word
                    unused_keywords.append(keyword.title())
                else:
                    unused_keywords.append(keyword)
        
        return unused_keywords
    except Exception as e:
        print(f"Error finding unused keywords: {e}")
        return []

def generate_resume(template_file, config_file, output_file, keywords_file=None, apply_formatting=True):
    """Generate resume from template and config"""
    print(f"Generating resume from {template_file}...")
    
    # Read template
    with open(template_file, 'r') as f:
        content = f.read()
    
    # Apply basic formatting
    if apply_formatting:
        content = fix_capitalization(content)
    
    # Add unused keywords if keywords file is provided
    if keywords_file and os.path.exists(keywords_file):
        unused_keywords = find_unused_keywords(content, keywords_file)
        
        if unused_keywords:
            # Check if Keywords section already exists
            keyword_match = re.search(r'## Keywords\s*\n\s*\n(.*?)(?=\n\s*\n##|\n*$)', content, re.DOTALL)
            
            if keyword_match:
                # Extract existing keywords
                existing_keywords = keyword_match.group(1).strip()
                # Combine with new keywords
                all_keywords = existing_keywords + ", " + ", ".join(unused_keywords)
                # Replace existing Keywords section content
                content = content.replace(keyword_match.group(0), f"## Keywords\n\n{all_keywords}")
            else:
                # No Keywords section found, add one at the end
                content = content.rstrip()
                content += "\n\n## Keywords\n\n"
                content += ", ".join(unused_keywords)
    
    # Write output
    with open(output_file, 'w') as f:
        f.write(content)
    
    print(f"Resume saved to {output_file}")
    return content

def get_google_drive_service():
    """Get authenticated Google Drive service."""
    creds = None
    # The file token.pickle stores the user's access and refresh tokens
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Look for client_secret.json file in the project root
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            client_secret_file = os.path.join(project_root, 'client_secret.json')
            
            if not os.path.exists(client_secret_file):
                raise FileNotFoundError("client_secret.json file not found in project root. Please add your Google API credentials.")
            flow = InstalledAppFlow.from_client_secrets_file(client_secret_file, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    service = build('drive', 'v3', credentials=creds)
    return service

def upload_to_drive(file_path, folder_id=DRIVE_FOLDER_ID):
    """Upload a file to Google Drive in the specified folder."""
    try:
        service = get_google_drive_service()
        
        file_name = os.path.basename(file_path)
        
        # Check if the file already exists
        query = f"name = '{file_name}' and '{folder_id}' in parents and trashed = false"
        results = service.files().list(q=query, fields="files(id, name)").execute()
        items = results.get('files', [])
        
        file_metadata = {
            'name': file_name,
            'parents': [folder_id]
        }
        
        media = MediaFileUpload(file_path, resumable=True)
        
        if items:
            # Update existing file
            file_id = items[0]['id']
            file = service.files().update(
                fileId=file_id,
                media_body=media,
                fields='id'
            ).execute()
            print(f"Updated existing file in Google Drive: {file_name}")
        else:
            # Create new file
            file = service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            print(f"Uploaded new file to Google Drive: {file_name}")
        
        # Get the file's web view link
        file_id = file.get('id')
        file_info = service.files().get(fileId=file_id, fields='webViewLink').execute()
        web_link = file_info.get('webViewLink')
        
        return web_link
    
    except Exception as e:
        print(f"Error uploading to Google Drive: {e}")
        return None

def generate_pdf(markdown_file, output_dir="."):
    """Generate PDF from markdown file using pandoc"""
    print("Generating PDF...")
    
    basename = os.path.basename(markdown_file)
    name_without_ext = os.path.splitext(basename)[0]
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Set PDF output path
    output_pdf = os.path.join(output_dir, f"{name_without_ext}.pdf")
    
    try:
        # Try to find pandoc
        result = subprocess.run("which pandoc", shell=True, capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            pandoc_path = result.stdout.strip()
        else:
            # Check common locations
            pandoc_paths = [
                "/usr/local/bin/pandoc",
                "/opt/homebrew/bin/pandoc",
                "/opt/homebrew/Cellar/pandoc/3.6.4/bin/pandoc" 
            ]
            
            pandoc_path = None
            for path in pandoc_paths:
                if os.path.exists(path) and os.access(path, os.X_OK):
                    pandoc_path = path
                    break
        
        if pandoc_path:
            print(f"Using pandoc: {pandoc_path}")
            # Run pandoc command with explicit pdflatex engine
            command = f"PATH=$PATH:/Library/TeX/texbin {pandoc_path} {markdown_file} -o {output_pdf} --pdf-engine=pdflatex"
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"PDF generation failed: {result.stderr}")
                return None
            else:
                print(f"PDF generated: {output_pdf}")
                return output_pdf
        else:
            print("Pandoc not found. Please install pandoc.")
            return None
        
    except Exception as e:
        print(f"Error: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description='Resume Generator for Job-Specific Optimization')
    parser.add_argument('--job-type', default='data_engineer', 
                      help='Job type (e.g., data_engineer, data_scientist)')
    parser.add_argument('--template', default='general', 
                      help='Template variant to use (e.g., general, pinterest, google)')
    parser.add_argument('--output', default='data/output/resume.md', 
                      help='Output resume markdown')
    parser.add_argument('--pdf', action='store_true', 
                      help='Generate PDF')
    parser.add_argument('--upload', action='store_true', 
                      help='Upload PDF to Google Drive')
    parser.add_argument('--basename', 
                      help='Base name for output files (e.g., "john_doe" will generate john_doe_resume.md)')
    
    args = parser.parse_args()
    
    # Set paths based on job type and template
    job_type_dir = os.path.join('job_types', args.job_type)
    keywords_file = os.path.join(job_type_dir, 'keywords.csv')
    template_file = os.path.join(job_type_dir, 'templates', f"{args.template}.md")
    
    # Check if job type directory exists
    if not os.path.exists(job_type_dir):
        print(f"Error: Job type '{args.job_type}' not found. Available job types:")
        job_types = [name for name in os.listdir('job_types') 
                    if os.path.isdir(os.path.join('job_types', name))]
        for jt in job_types:
            print(f"  - {jt}")
        return
    
    # Check if template exists
    if not os.path.exists(template_file):
        print(f"Error: Template '{args.template}' not found for job type '{args.job_type}'. Available templates:")
        templates_dir = os.path.join(job_type_dir, 'templates')
        if os.path.exists(templates_dir):
            templates = [os.path.splitext(name)[0] for name in os.listdir(templates_dir) 
                        if name.endswith('.md')]
            for t in templates:
                print(f"  - {t}")
        return
    
    # Check if keywords file exists
    if not os.path.exists(keywords_file):
        print(f"Error: Keywords file not found for job type '{args.job_type}'.")
        return
    
    # Create output directory if needed
    output_dir = os.path.dirname(args.output)
    os.makedirs(output_dir, exist_ok=True)
    
    # Set base filename if specified
    if args.basename:
        # Convert spaces to underscores and make lowercase
        basename = args.basename.replace(' ', '_').lower()
        # Get the original filename extension
        _, ext = os.path.splitext(args.output)
        # Set new output path with basename
        base_output = os.path.join(output_dir, f"{basename}_resume{ext}")
    else:
        base_output = args.output
    
    # Process keywords
    keywords_output = os.path.join(output_dir, 'processed_keywords.csv')
    keywords = process_keywords(keywords_file, keywords_output)
    
    # Generate resume from template, passing the keywords file
    generate_resume(template_file, None, base_output, keywords_file=keywords_output)
    
    # Generate PDF if requested
    pdf_file = None
    if args.pdf:
        pdf_output = output_dir
        pdf_file = generate_pdf(base_output, pdf_output)
        if pdf_file:
            print(f"Resume PDF available at: {pdf_file}")
        else:
            print("PDF generation failed.")
    
    # Upload to Google Drive if requested
    if args.upload and pdf_file:
        print("Uploading to Google Drive...")
        drive_link = upload_to_drive(pdf_file)
        if drive_link:
            print(f"Resume uploaded to Google Drive: {drive_link}")
        else:
            print("Upload to Google Drive failed.")
    
    print("Resume generation complete!")

if __name__ == "__main__":
    main()