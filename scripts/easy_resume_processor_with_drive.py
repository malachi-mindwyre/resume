#!/usr/bin/env python3
"""
Easy Resume Processor with Google Drive Integration

This script performs the complete resume processing workflow with Google Drive integration:
1. Download a Google Sheet to CSV
2. Process keywords from the CSV
3. Update resume with keywords
4. Generate PDF
5. Upload the PDF to Google Drive

Requires Google API authentication with proper permissions.
"""

import os
import sys
import subprocess
import pandas as pd
import datetime
import time
import argparse

# Get script directory and base path
script_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.dirname(script_dir)
os.chdir(base_dir)  # Change to the base directory

# Add both base dir and scripts dir to path
sys.path.append(base_dir)
sys.path.append(script_dir)

# Configure logging
def log(message, level="INFO"):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {level}: {message}")

def main():
    print("===== Resume Processing with Google Drive Integration =====")
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Process resume with Google Drive integration')
    parser.add_argument('--skip-download', action='store_true', help='Skip downloading from Google Sheet')
    parser.add_argument('--skip-upload', action='store_true', help='Skip uploading to Google Drive')
    parser.add_argument('--sheet-id', default='1C20hzxMQzT310HSe9DhH8XigArW5VcjAGgQfGafF4o4', 
                        help='Google Sheet ID')
    parser.add_argument('--folder-id', default='1s6n9eS9d2NNy9lyXgoYdPGOwkyGGujnw', 
                        help='Google Drive folder ID')
    
    args = parser.parse_args()

    # Configuration parameters
    config = {
        # Input files
        "input_keywords_file": "data/input/lead_gen.csv",        # Raw keywords input
        
        # Output files
        "processed_keywords_file": "data/output/processed_keywords.csv", # Processed keywords output
        "output_resume_name": "resume",                      # Base name for output files
        
        # Directory structure
        "templates_dir": "templates",                        # Directory for template markdown files
        "output_dir": "data/output",                         # Directory for output files
        
        # Options
        "top_keywords": 20,                                  # Number of top keywords to highlight
        "generate_pdf": True,                                # Try to generate PDF
        
        # Google Drive settings
        "sheet_id": args.sheet_id,                           # Google Sheet ID
        "folder_id": args.folder_id,                         # Google Drive folder ID
        "skip_download": args.skip_download,                 # Skip downloading from Google
        "skip_upload": args.skip_upload,                     # Skip uploading to Google
    }

    # Set file paths based on configuration
    config["input_resume_file"] = os.path.join(config["templates_dir"], f"{config['output_resume_name']}.md")
    config["output_resume_file"] = os.path.join(config["output_dir"], f"{config['output_resume_name']}.md")
    config["output_pdf_file"] = os.path.join(config["output_dir"], f"{config['output_resume_name']}.pdf")

    # Print configuration
    print("\n===== Configuration =====")
    for key, value in config.items():
        log(f"Config: {key} = {value}")

    # Create directory structure
    os.makedirs(config["templates_dir"], exist_ok=True)
    os.makedirs(config["output_dir"], exist_ok=True)
    os.makedirs(os.path.dirname(config["input_keywords_file"]), exist_ok=True)

    # Import modules
    import scripts.keywords_processor as keywords_processor
    import scripts.update_resume as update_resume
    import scripts.google_drive_handler as google_drive

    # Step 1: Download from Google Drive (if not skipped)
    if not config["skip_download"]:
        print("\n===== Step 1: Download from Google Drive =====")
        log(f"Downloading Google Sheet {config['sheet_id']} to {config['input_keywords_file']}...")
        
        success = google_drive.download_spreadsheet(
            config["sheet_id"], 
            config["input_keywords_file"]
        )
        
        if success:
            log("Google Sheet downloaded successfully")
        else:
            log("Failed to download Google Sheet. Using existing file if available.", "WARNING")
    else:
        log("Skipping Google Drive download based on configuration")

    # Step 2: Process keywords
    print("\n===== Step 2: Process Keywords =====")
    log("Starting keyword processing...")

    # Check if input file exists
    if os.path.exists(config["input_keywords_file"]):
        size = os.path.getsize(config["input_keywords_file"])
        log(f"Input file exists: {config['input_keywords_file']} (Size: {size} bytes)")
    else:
        log(f"Input keywords file not found: {config['input_keywords_file']}", "ERROR")
        sys.exit(1)

    # Process keywords
    start_time = time.time()
    log(f"Processing keywords from {config['input_keywords_file']}...")
    high_df, low_df = keywords_processor.process_keywords(
        config["input_keywords_file"], 
        config["processed_keywords_file"]
    )
    end_time = time.time()
    log(f"Keywords processed in {end_time - start_time:.2f} seconds")

    # Display top keywords
    print("\n===== Top High-Priority Keywords =====")
    print(high_df.head(config["top_keywords"]).to_string(index=False))
    print("\n===== Top Low-Priority Keywords =====")
    print(low_df.head(config["top_keywords"]).to_string(index=False))

    # Step 3: Update resume
    print("\n===== Step 3: Update Resume =====")
    log("Starting resume update...")

    # Load top keywords
    keywords_df = pd.read_csv(config["processed_keywords_file"])
    high_priority = keywords_df[(keywords_df['priority'] == 'high')].sort_values('count', ascending=False).head(config["top_keywords"])
    keywords = high_priority['keyword'].tolist()

    log(f"Updating resume with top {len(keywords)} keywords")
    for i, keyword in enumerate(keywords):
        log(f"Keyword {i+1}: {keyword} (Count: {high_priority.iloc[i]['count']})")

    # Update resume with keywords
    start_time = time.time()
    update_resume.highlight_keywords(
        config["input_resume_file"],
        config["output_resume_file"],
        keywords
    )
    end_time = time.time()
    log(f"Resume updated in {end_time - start_time:.2f} seconds")

    # Step 4: Generate PDF
    print("\n===== Step 4: Generate PDF =====")
    pdf_path = None
    if config["generate_pdf"]:
        log("Starting PDF generation...")
        try:
            # Try to generate PDF using update_resume module
            pdf_path = update_resume.generate_pdf(
                config["output_resume_file"],
                config["output_dir"]
            )
            
            # Check if PDF was generated successfully
            if pdf_path and os.path.exists(pdf_path):
                log(f"PDF generation complete: {pdf_path}")
            else:
                # If not, check if PDF exists from previous runs
                default_pdf_path = os.path.join(config["output_dir"], f"{config['output_resume_name']}.pdf")
                if os.path.exists(default_pdf_path):
                    log(f"Using existing PDF: {default_pdf_path}", "WARNING")
                    pdf_path = default_pdf_path
                else:
                    log("PDF generation failed and no existing PDF found.", "WARNING")
                    log("Consider using VS Code with Markdown PDF extension", "INFO")
        except Exception as e:
            log(f"Error during PDF generation: {e}", "ERROR")
            # Check if PDF exists despite the error
            default_pdf_path = os.path.join(config["output_dir"], f"{config['output_resume_name']}.pdf")
            if os.path.exists(default_pdf_path):
                log(f"Using existing PDF despite error: {default_pdf_path}", "WARNING")
                pdf_path = default_pdf_path
    else:
        log("PDF generation skipped based on configuration")

    # Step 5: Upload to Google Drive (if not skipped)
    if not config["skip_upload"] and pdf_path and os.path.exists(pdf_path):
        print("\n===== Step 5: Upload to Google Drive =====")
        log(f"Uploading PDF {pdf_path} to Google Drive folder {config['folder_id']}...")
        
        web_link = google_drive.upload_pdf_to_drive(
            pdf_path, 
            config["folder_id"]
        )
        
        if web_link:
            log("PDF uploaded successfully")
            log(f"Access your PDF at: {web_link}")
        else:
            log("Failed to upload PDF to Google Drive", "WARNING")
    else:
        if config["skip_upload"]:
            log("Skipping Google Drive upload based on configuration")
        elif not pdf_path or not os.path.exists(pdf_path):
            log("Skipping Google Drive upload because PDF was not generated", "WARNING")

    # Summary
    print("\n===== Summary =====")
    log("Resume processing complete!")
    
    print("\nProcessing Summary:")
    print(f"Input keywords file: {config['input_keywords_file']}")
    print(f"Processed keywords file: {config['processed_keywords_file']}")
    print(f"Resume markdown file: {config['output_resume_file']}")
    
    if config["generate_pdf"] and pdf_path and os.path.exists(pdf_path):
        print(f"Generated PDF: {pdf_path}")
    
    if not config["skip_upload"] and pdf_path and os.path.exists(pdf_path) and web_link:
        print(f"Uploaded PDF: {web_link}")

    print("\nTop 10 Keywords Used:")
    for i, keyword in enumerate(keywords[:10]):
        print(f"{i+1}. {keyword} (Count: {high_priority.iloc[i]['count']})")

    print("\n===== All processing completed successfully =====")

if __name__ == "__main__":
    main()