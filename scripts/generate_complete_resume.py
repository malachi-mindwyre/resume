#!/usr/bin/env python3
"""
Complete Resume Generator

This script handles the full resume generation workflow:
1. Generate the resume structure from configuration
2. Process the resume with keywords
3. Generate a PDF

Usage:
  python generate_complete_resume.py --config templates/resume_config.yaml --keywords data/output/processed_keywords.csv --output data/output/resume.md
"""

import os
import sys
import argparse
import yaml

# Add script directory to path
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_dir)

# Import local modules
import resume_generator
import update_resume

def main():
    parser = argparse.ArgumentParser(description="Generate a complete resume with processed keywords")
    parser.add_argument('--config', default='templates/resume_config.yaml', help='Resume configuration file')
    parser.add_argument('--keywords', default='data/output/processed_keywords.csv', help='Processed keywords CSV file')
    parser.add_argument('--output', default='data/output/resume.md', help='Output resume markdown file')
    parser.add_argument('--content-dir', help='Directory containing section content files')
    parser.add_argument('--pdf-dir', default='data/output', help='Directory for PDF output')
    parser.add_argument('--no-pdf', action='store_true', help='Skip PDF generation')
    
    args = parser.parse_args()
    
    # Create necessary directories
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    
    # Step 1: Generate resume structure from config
    print(f"Step 1: Generating resume structure from {args.config}...")
    config = resume_generator.load_config(args.config)
    resume_generator.generate_resume(config, args.output, args.content_dir)
    
    # Step 2: Process resume with keywords
    print(f"Step 2: Processing resume with keywords from {args.keywords}...")
    keywords = []
    if os.path.exists(args.keywords):
        # Load top keywords
        try:
            import pandas as pd
            keywords_df = pd.read_csv(args.keywords)
            high_priority = keywords_df[(keywords_df['priority'] == 'high')].sort_values('count', ascending=False).head(20)
            keywords = high_priority['keyword'].tolist()
            print(f"Loaded {len(keywords)} high-priority keywords")
        except Exception as e:
            print(f"Error loading keywords: {e}")
    else:
        print(f"Keywords file not found: {args.keywords}")
    
    # Process the resume
    update_resume.highlight_keywords(args.output, args.output, keywords)
    
    # Step 3: Generate PDF (unless skipped)
    if not args.no_pdf:
        print("Step 3: Generating PDF...")
        pdf_path = update_resume.generate_pdf(args.output, args.pdf_dir)
        if pdf_path:
            print(f"PDF generated successfully: {pdf_path}")
        else:
            print("PDF generation failed")
    else:
        print("Step 3: PDF generation skipped")
    
    print(f"\nResume generation complete!\nResume saved to: {args.output}")

if __name__ == "__main__":
    main()