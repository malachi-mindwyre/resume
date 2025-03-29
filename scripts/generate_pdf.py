#!/usr/bin/env python3
"""
Standalone script to generate PDF from a markdown file using pandoc
"""

import os
import subprocess
import sys
import re

def fix_markdown_escapes(markdown_file, fixed_file):
    """
    Fix markdown escape sequences that might cause issues in LaTeX processing
    """
    with open(markdown_file, 'r') as f:
        content = f.read()
    
    # First, let's handle the YAML frontmatter
    # If the content starts with ---, we should remove or replace it with a simpler version
    if content.startswith('---'):
        # Find the end of frontmatter
        frontmatter_end = content.find('---', 3)
        if frontmatter_end > 0:
            # Remove the existing frontmatter
            content = content[frontmatter_end + 3:].strip()
    
    # Add a simpler frontmatter
    simple_frontmatter = """---
mainfont: DejaVu Sans
geometry: margin=1in
output: pdf_document
---

"""
    fixed_content = simple_frontmatter + content
    
    # Fix Markdown backslash escapes that are problematic in LaTeX
    fixed_content = fixed_content.replace('\\_', '_')
    fixed_content = fixed_content.replace('\\&', '&')
    
    # We'll handle backslashes more carefully - don't double escape already escaped sequences
    # fixed_content = fixed_content.replace('\\', '\\\\')  # Escape backslashes for LaTeX
    
    # Write the fixed content to a temporary file
    with open(fixed_file, 'w') as f:
        f.write(fixed_content)
    
    return fixed_file

def generate_pdf(markdown_file, output_dir=None):
    """Generate PDF from markdown file using pandoc"""
    print(f"Generating PDF from {markdown_file}...")
    
    if output_dir is None:
        output_dir = os.path.dirname(markdown_file) or '.'
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Get file basename without extension
    basename = os.path.basename(markdown_file)
    name_without_ext = os.path.splitext(basename)[0]
    
    # Create a fixed version of the markdown file
    fixed_file = os.path.join(output_dir, f"{name_without_ext}_fixed.md")
    fix_markdown_escapes(markdown_file, fixed_file)
    
    # Set PDF output path
    output_pdf = os.path.join(output_dir, f"{name_without_ext}.pdf")
    
    try:
        # Find pandoc
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
                    
        if not pandoc_path:
            print("Pandoc not found. Please install pandoc.")
            return None
            
        print(f"Using pandoc: {pandoc_path}")
        
        # Run pandoc with explicit options to handle escapes properly
        command = (
            f"PATH=$PATH:/Library/TeX/texbin "
            f"{pandoc_path} {fixed_file} -o {output_pdf} "
            f"--pdf-engine=pdflatex -V geometry:margin=1in"
        )
        
        print(f"Running command: {command}")
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"PDF generation failed: {result.stderr}")
            return None
        else:
            print(f"PDF generated successfully: {output_pdf}")
            return output_pdf
            
    except Exception as e:
        print(f"Error generating PDF: {e}")
        return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate_pdf.py <markdown_file> [output_directory]")
        sys.exit(1)
        
    markdown_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(markdown_file):
        print(f"Error: File {markdown_file} not found")
        sys.exit(1)
        
    pdf_file = generate_pdf(markdown_file, output_dir)
    
    if pdf_file:
        print(f"PDF successfully generated at: {pdf_file}")
        sys.exit(0)
    else:
        print("PDF generation failed")
        sys.exit(1)