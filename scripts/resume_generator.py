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
import sys # Added for error exit
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload
from PyPDF2 import PdfReader # Added for PDF parsing
import docx # Added for DOCX parsing

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

# --- Resume Parsing Functions ---

def parse_pdf(file_path):
    """Extract text content from a PDF file."""
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or "" # Add empty string if extraction fails for a page
        return text
    except Exception as e:
        print(f"Error parsing PDF file {file_path}: {e}")
        return None

def parse_docx(file_path):
    """Extract text content from a DOCX file."""
    try:
        doc = docx.Document(file_path)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text
    except Exception as e:
        print(f"Error parsing DOCX file {file_path}: {e}")
        return None

def parse_markdown(file_path):
    """Read content from a Markdown file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading Markdown file {file_path}: {e}")
        return None

def parse_resume(file_path):
    """Parse resume file based on its extension."""
    _, extension = os.path.splitext(file_path.lower())
    print(f"Attempting to parse resume file: {file_path} (type: {extension})")
    if extension == '.pdf':
        return parse_pdf(file_path)
    elif extension == '.docx':
        return parse_docx(file_path)
    elif extension == '.md':
        return parse_markdown(file_path)
    else:
        print(f"Error: Unsupported file type '{extension}'. Please use PDF, DOCX, or MD.")
        return None

def parse_structured_resume(file_path):
    """Attempt to parse resume into sections and bullet points (focus on Markdown)."""
    content = parse_resume(file_path)
    if content is None:
        return None

    structure = {}
    current_section = "Header" # Default section for content before first heading
    structure[current_section] = []

    # Regex to find Markdown headings (## Section Name) and bullet points (* or -)
    # This is a simplified approach and might need refinement
    section_pattern = re.compile(r'^\s*##\s+(.*?)\s*$', re.MULTILINE)
    bullet_pattern = re.compile(r'^\s*[\*\-]\s+(.*)', re.MULTILINE)

    last_pos = 0
    for match in section_pattern.finditer(content):
        # Add text between the last match/start and this heading to the previous section
        intermediate_text = content[last_pos:match.start()].strip()
        if intermediate_text:
             # Try to find bullets in the intermediate text
             bullets_in_intermediate = [m.group(1).strip() for m in bullet_pattern.finditer(intermediate_text)]
             if bullets_in_intermediate:
                 structure[current_section].extend(bullets_in_intermediate)
             elif current_section == "Header": # Add non-bullet text only to header initially
                 structure[current_section].append(intermediate_text)


        # Start new section
        current_section = match.group(1).strip()
        if current_section not in structure:
            structure[current_section] = []
        last_pos = match.end()

    # Process text after the last heading
    final_text = content[last_pos:].strip()
    if final_text:
        bullets_in_final = [m.group(1).strip() for m in bullet_pattern.finditer(final_text)]
        if bullets_in_final:
            structure[current_section].extend(bullets_in_final)
        elif current_section == "Header": # Add non-bullet text only to header
             structure[current_section].append(final_text)
        # Optionally add non-bullet text to other sections if needed
        # else:
        #    structure[current_section].append(final_text)


    # Basic cleanup: remove empty sections, maybe merge header if only contains whitespace
    structure = {k: v for k, v in structure.items() if v}
    if "Header" in structure and not any(s.strip() for s in structure["Header"]):
        del structure["Header"]

    print(f"Parsed structure with sections: {list(structure.keys())}")
    return structure


def calculate_keyword_coverage(resume_content, keywords_df):
    """Calculate the percentage of keywords from the DataFrame found in the resume content."""
    if keywords_df.empty or not resume_content:
        return 0.0, [], [] # Coverage percentage, found keywords, missing keywords

    found_keywords = []
    missing_keywords = []
    resume_lower = resume_content.lower()
    total_keywords = len(keywords_df)

    if total_keywords == 0:
        return 0.0, [], []

    for _, row in keywords_df.iterrows():
        keyword = row['keyword']
        if not isinstance(keyword, str) or len(keyword) < 2:
            total_keywords -= 1 # Adjust total count for invalid keywords
            continue

        # Use regex for whole word matching, case-insensitive
        pattern = r'(?i)\b' + re.escape(keyword) + r'\b'
        if re.search(pattern, resume_content):
            found_keywords.append(keyword)
        else:
            missing_keywords.append(keyword)

    if total_keywords == 0: # Avoid division by zero if all keywords were invalid
         return 0.0, [], []

    coverage_percentage = (len(found_keywords) / total_keywords) * 100
    return coverage_percentage, found_keywords, missing_keywords

def analyze_keyword_distribution(structured_data, keywords_df):
    """Analyze the distribution of keywords across resume sections."""
    if keywords_df.empty or not structured_data:
        return {} # Return empty dict if no keywords or data

    distribution = {}
    all_keywords_set = set(keywords_df['keyword'].str.lower())

    for section, items in structured_data.items():
        section_content = "\n".join(items)
        section_lower = section_content.lower()
        found_in_section = []

        for keyword in all_keywords_set:
             # Use regex for whole word matching, case-insensitive
             pattern = r'(?i)\b' + re.escape(keyword) + r'\b'
             if re.search(pattern, section_content): # Search in original case content for pattern
                 found_in_section.append(keyword)

        if found_in_section:
            # Store the count and the list of keywords found in this section
            distribution[section] = {
                'count': len(found_in_section),
                'keywords': sorted(list(set(found_in_section))) # Store unique keywords found
            }

    print(f"Keyword distribution analyzed: { {k: v['count'] for k, v in distribution.items()} }")
    return distribution

# --- Keyword Loading ---

def load_keywords_for_job(job_type, keywords_db_file='keywords_db.csv'):
    """Load and filter keywords for a specific job type from the central DB."""
    print(f"Loading keywords for job type '{job_type}' from {keywords_db_file}...")
    if not os.path.exists(keywords_db_file):
        print(f"Error: Keywords DB file not found at {keywords_db_file}")
        return pd.DataFrame() # Return empty DataFrame

    try:
        df = pd.read_csv(keywords_db_file)
        # Ensure roles column is string type
        df['roles'] = df['roles'].astype(str)
        # Filter keywords where the job_type is present in the 'roles' column (comma-separated)
        # Use regex word boundary \b to match whole job type code
        filtered_df = df[df['roles'].str.contains(r'\b' + re.escape(job_type) + r'\b', na=False)]
        # Sort by weight descending
        filtered_df = filtered_df.sort_values(by='weight', ascending=False)
        print(f"Loaded {len(filtered_df)} keywords for job type '{job_type}'.")
        return filtered_df[['keyword', 'weight']] # Return relevant columns
    except Exception as e:
        print(f"Error loading or processing keywords DB: {e}")
        return pd.DataFrame()

def fix_capitalization(content):
    """Fix capitalization of specific terms - Tries to use SPECIAL_TERMS first"""
    
    # For each special term, replace it with proper capitalization
    for term, capitalized in SPECIAL_TERMS.items():
        # Use regex to match the term as a whole word, case-insensitive
        # Ensure it doesn't match within another word
        pattern = r'(?i)\b' + re.escape(term) + r'\b'
        # Use a lambda function to preserve original case if replacement is identical ignoring case
        # This prevents changing 'SQLAlchemy' to 'Sqlalchemy' if 'sql' is a special term
        content = re.sub(pattern, lambda match: capitalized if match.group(0).lower() == term else match.group(0), content)
    
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

def find_unused_keywords(resume_content, keywords_df):
    """Find keywords from the provided DataFrame that aren't in the resume content."""
    if keywords_df.empty:
        return []

    # Convert resume content to lowercase for comparison
    resume_lower = resume_content.lower()
    unused_keywords_list = []

    for _, row in keywords_df.iterrows():
        keyword = row['keyword']
        # Basic check for keyword validity
        if not isinstance(keyword, str) or len(keyword) < 2: # Skip very short/invalid keywords
            continue

        # Use regex for whole word matching, case-insensitive
        # This prevents matching 'pythonic' if keyword is 'python'
        pattern = r'(?i)\b' + re.escape(keyword) + r'\b'
        if not re.search(pattern, resume_content):
            # Use the original casing from the keywords_df
            unused_keywords_list.append(keyword)

    # Consider adding prioritization based on weight here in the future
    # For now, return all unused keywords from the filtered list
    return unused_keywords_list


# Renamed and modified function to accept structured data
def generate_resume_from_structure(edited_data, output_file, keywords_df, apply_formatting=True):
    """Generate resume Markdown from structured edited data and keywords."""
    print(f"Generating resume from edited structure...")
    content_parts = []

    # Define preferred section order (similar to UI builder)
    preferred_order = ['Header', 'Profile Summary', 'Technical Skills', 'Professional Experience', 'Projects Experience', 'Education', 'Certifications', 'Publications', 'Keywords']
    # Get keys from edited_data, handling potential missing keys during sorting
    section_keys = sorted(edited_data.keys(), key=lambda x: preferred_order.index(x) if x in preferred_order else len(preferred_order))

    # Reconstruct Markdown content
    for section_name in section_keys:
        items = edited_data.get(section_name, []) # Use .get for safety
        if not items: # Skip empty sections
            continue

        # Add section header (unless it's the implicit 'Header')
        if section_name != "Header":
             # Add extra newline before section headers for spacing, except for the very first section if it's not Header
             if content_parts:
                 content_parts.append("") # Add blank line
             content_parts.append(f"## {section_name}")

        # Add items/bullets
        for item in items:
            item_strip = item.strip()
            if not item_strip: # Skip empty items
                continue
            # Check if item looks like a bullet point already
            if item_strip.startswith(('-', '*')):
                 content_parts.append(item_strip)
            else:
                 # Assume non-bullet items are paragraphs or need bullet prefix
                 # Simple approach: add bullet prefix if it's likely list item in certain sections
                 if section_name in ['Professional Experience', 'Projects Experience', 'Technical Skills', 'Certifications']: # Added more sections likely to use bullets
                     content_parts.append(f"- {item_strip}")
                 else: # Assume paragraph or header content
                     content_parts.append(item_strip) # Keep as is for Header, Profile, Education etc.

    reconstructed_content = "\n".join(content_parts)

    # Apply basic formatting (like capitalization)
    if apply_formatting:
        reconstructed_content = fix_capitalization(reconstructed_content) # Apply capitalization fixes first

    # Find and add unused keywords to the reconstructed content
    final_content = reconstructed_content # Start with reconstructed
    if not keywords_df.empty:
        # Use the reconstructed content for finding unused keywords
        unused_keywords = find_unused_keywords(reconstructed_content, keywords_df)

        if unused_keywords:
             # Format keywords nicely
             formatted_unused = []
             for kw in unused_keywords:
                  lower_kw = kw.lower()
                  if lower_kw in SPECIAL_TERMS:
                      formatted_unused.append(SPECIAL_TERMS[lower_kw])
                  else:
                      if kw.islower():
                          formatted_unused.append(kw.title())
                      else:
                          formatted_unused.append(kw)

             keyword_string = ", ".join(sorted(list(set(formatted_unused)), key=str.lower))

             # Check if Keywords section already exists in the *reconstructed* content
             # Use MULTILINE flag and anchors ^ $
             keyword_section_pattern = re.compile(r'(^\s*##\s*Keywords\s*\n+)(.*?)(\n*\s*(##|$))', re.DOTALL | re.MULTILINE | re.IGNORECASE)
             match = keyword_section_pattern.search(reconstructed_content)

             if match:
                 # Section exists, append new keywords if not already present
                 existing_keywords_text = match.group(2).strip()
                 existing_keywords_list = [kw.strip() for kw in existing_keywords_text.split(',') if kw.strip()]
                 combined_keywords = sorted(list(set(existing_keywords_list + formatted_unused)), key=str.lower)
                 # Ensure proper formatting in the replacement
                 new_keyword_section_content = f"{match.group(1)}{', '.join(combined_keywords)}\n{match.group(3)}"
                 # Replace in the final_content
                 final_content = keyword_section_pattern.sub(new_keyword_section_content, reconstructed_content, count=1)
                 print(f"Appended {len(formatted_unused)} unique keywords to existing Keywords section.")
             else:
                 # Section doesn't exist, add it to the end
                 final_content = reconstructed_content.rstrip() + f"\n\n## Keywords\n\n{keyword_string}"
                 print(f"Added new Keywords section with {len(formatted_unused)} keywords.")

    # Write the final, potentially keyword-enhanced, content
    try:
        with open(output_file, 'w') as f:
            f.write(final_content)
        print(f"Resume saved to {output_file}")
        return final_content
    except Exception as e:
        print(f"Error writing output file {output_file}: {e}")
        return None

def save_structure_as_template(structured_data, output_template_file):
    """Saves the structured resume data as a Markdown template file."""
    print(f"Saving structure as new template: {output_template_file}")
    content_parts = []
    # Use the same preferred order as generation
    preferred_order = ['Header', 'Profile Summary', 'Technical Skills', 'Professional Experience', 'Projects Experience', 'Education', 'Certifications', 'Publications', 'Keywords']
    section_keys = sorted(structured_data.keys(), key=lambda x: preferred_order.index(x) if x in preferred_order else len(preferred_order))

    # Reconstruct Markdown content
    for section_name in section_keys:
        items = structured_data.get(section_name, [])
        if not items and section_name != "Keywords": # Keep Keywords section even if empty initially
             continue

        if section_name != "Header":
             if content_parts:
                 content_parts.append("")
             content_parts.append(f"## {section_name}")

        for item in items:
            item_strip = item.strip()
            if not item_strip:
                continue
            if item_strip.startswith(('-', '*')):
                 content_parts.append(item_strip)
            else:
                 # Add bullet for list-like sections, otherwise keep as paragraph
                 if section_name in ['Professional Experience', 'Projects Experience', 'Technical Skills', 'Certifications']:
                     content_parts.append(f"- {item_strip}")
                 else:
                     content_parts.append(item_strip)

    template_content = "\n".join(content_parts)

    try:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(output_template_file), exist_ok=True)
        with open(output_template_file, 'w') as f:
            f.write(template_content)
        print(f"Template saved successfully: {output_template_file}")
        return True
    except Exception as e:
        print(f"Error saving template file {output_template_file}: {e}")
        return False


# --- Keep original generate_resume for now as fallback or for non-interactive use? ---
# Or remove it if generate_resume_from_structure is the only path forward.
# For now, let's keep it but note it's deprecated for the interactive flow.

def generate_resume(template_file, config_file, output_file, keywords_df, apply_formatting=True):
    """Generate resume from template file (DEPRECATED for interactive flow)."""
    print(f"WARNING: Using deprecated generate_resume from template file: {template_file}...")
    # This function remains largely the same as before the structure changes
    try:
        with open(template_file, 'r') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading template file {template_file}: {e}")
        return None

    if apply_formatting:
        content = fix_capitalization(content)

    if not keywords_df.empty:
        unused_keywords = find_unused_keywords(content, keywords_df)
        if unused_keywords:
            formatted_unused = []
            for kw in unused_keywords:
                 lower_kw = kw.lower()
                 if lower_kw in SPECIAL_TERMS:
                     formatted_unused.append(SPECIAL_TERMS[lower_kw])
                 else:
                     if kw.islower():
                         formatted_unused.append(kw.title())
                     else:
                         formatted_unused.append(kw)
            keyword_string = ", ".join(sorted(list(set(formatted_unused)), key=str.lower))
            keyword_section_pattern = re.compile(r'(^\s*##\s*Keywords\s*\n+)(.*?)(\n*\s*(##|$))', re.DOTALL | re.MULTILINE | re.IGNORECASE)
            match = keyword_section_pattern.search(content)
            if match:
                existing_keywords_text = match.group(2).strip()
                existing_keywords_list = [kw.strip() for kw in existing_keywords_text.split(',') if kw.strip()]
                combined_keywords = sorted(list(set(existing_keywords_list + formatted_unused)), key=str.lower)
                new_keyword_section_content = f"{match.group(1)}{', '.join(combined_keywords)}\n{match.group(3)}"
                content = keyword_section_pattern.sub(new_keyword_section_content, content, count=1)
            else:
                content = content.rstrip() + f"\n\n## Keywords\n\n{keyword_string}"

    try:
        with open(output_file, 'w') as f:
            f.write(content)
        print(f"Resume saved to {output_file}")
        return content
    except Exception as e:
        print(f"Error writing output file {output_file}: {e}")
        return None


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
            
            # NOTE: These are common macOS paths. Users on other OSes (Linux/Windows)
            # may need to ensure pandoc is installed and accessible via their system's PATH,
            # or modify this path detection logic.
            pandoc_path = None
            for path in pandoc_paths:
                if os.path.exists(path) and os.access(path, os.X_OK):
                    pandoc_path = path
                    break

        if pandoc_path:
            print(f"Using pandoc: {pandoc_path}")
            # Run pandoc command with explicit pdflatex engine
            # NOTE: Assumes pdflatex (from a TeX distribution like MacTeX/MiKTeX/TeX Live)
            # is available in the system's PATH or a common location like /Library/TeX/texbin (macOS).
            # Users may need to install a TeX distribution.
            # The PATH modification below is specific to macOS with MacTeX.
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

    # --- Updated Path Logic ---
    job_type_dir = os.path.join('job_types', args.job_type) # Still needed for templates
    template_file = os.path.join(job_type_dir, 'templates', f"{args.template}.md")
    keywords_db_file = 'keywords_db.csv' # Central keywords DB

    # Check if job type directory exists (for templates)
    # (Validation logic remains similar)
    if not os.path.exists(job_type_dir):
        print(f"Error: Job type directory '{args.job_type}' not found (needed for templates). Available job types:")
        # ... (listing job types remains the same) ...
        sys.exit(1) # Exit script on error

    # Check if template exists
    # (Validation logic remains similar)
    # ... (listing templates remains the same) ...
        sys.exit(1) # Exit script on error

    # --- Removed check for old keywords file ---

    # Check if central keywords DB exists
    if not os.path.exists(keywords_db_file):
        print(f"Error: Central keywords database '{keywords_db_file}' not found.")
        sys.exit(1) # Exit script on error

    # Create output directory if needed
    # (Logic remains the same)
    # (Logic remains the same)

    # --- Updated Keyword Loading and Resume Generation ---
    # Load keywords for the specified job type
    keywords_df = load_keywords_for_job(args.job_type, keywords_db_file)

    if keywords_df.empty and args.job_type: # Check if loading failed or returned empty
         print(f"Warning: No keywords loaded for job type '{args.job_type}'. Proceeding without keyword analysis.")

    # --- Command Line uses the old template-based generation ---
    # The interactive structure generation is only triggered via the notebook for now.
    # If CLI needs structure support, parse_structured_resume would need integration here.
    print(f"Note: Command-line execution uses the template file '{template_file}' directly.")
    generated_content = generate_resume(template_file, None, base_output, keywords_df=keywords_df)

    if generated_content is None:
        print("Resume generation failed.")
        sys.exit(1) # Exit if resume generation itself failed

    # Generate PDF if requested
    # (Logic remains the same)
    # (Logic remains the same)

    # Upload to Google Drive if requested
    # (Logic remains the same)

    print("Resume generation process complete!")

if __name__ == "__main__":
    main()
