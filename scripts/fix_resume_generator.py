#!/usr/bin/env python3
"""
Fixed Resume Generator to address the base_output variable issue
"""

import pandas as pd
import os
import re
import subprocess
import yaml
import argparse
import sys
from resume_generator import (
    load_keywords_for_job, generate_resume, generate_pdf
)

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
    parser.add_argument('--basename',
                      help='Base name for output files (e.g., "john_doe" will generate john_doe_resume.md)')

    args = parser.parse_args()

    # Set up output path
    output_dir = os.path.dirname(args.output)
    os.makedirs(output_dir, exist_ok=True)
    
    # Define base output path
    if args.basename:
        base_output = os.path.join(output_dir, f"{args.basename}_resume.md")
    else:
        base_output = args.output

    # Path setup
    project_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
    job_type_dir = os.path.join(project_root, 'job_types', args.job_type)
    template_file = os.path.join(job_type_dir, 'templates', f"{args.template}.md")
    keywords_db_file = os.path.join(project_root, 'keywords_db.csv')

    # Check if job type directory exists
    if not os.path.exists(job_type_dir):
        print(f"Error: Job type directory '{args.job_type}' not found.")
        sys.exit(1)

    # Check if template exists
    if not os.path.exists(template_file):
        print(f"Error: Template '{args.template}' not found for job type '{args.job_type}'.")
        sys.exit(1)

    # Load keywords
    keywords_df = load_keywords_for_job(args.job_type, keywords_db_file)
    if keywords_df.empty:
        print(f"Warning: No keywords loaded for job type '{args.job_type}'. Proceeding without keyword analysis.")

    # Generate resume
    print(f"Generating resume using template '{template_file}'...")
    generated_content = generate_resume(template_file, None, base_output, keywords_df=keywords_df)
    if generated_content is None:
        print("Resume generation failed.")
        sys.exit(1)
    
    print(f"Resume generated: {base_output}")

    # Generate PDF if requested
    if args.pdf:
        print("Generating PDF...")
        pdf_file = generate_pdf(base_output, output_dir)
        if pdf_file:
            print(f"PDF generated: {pdf_file}")
        else:
            print("PDF generation failed.")

if __name__ == "__main__":
    main()