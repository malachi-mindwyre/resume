#!/usr/bin/env python3
"""
Advanced PDF Generator for resumes with custom LaTeX formatting

This script preserves advanced LaTeX formatting used in templates like malachi_dunn_general.md,
including custom colors, section formatting, centering, and other LaTeX-specific features.
"""

import os
import subprocess
import sys
import re

def preserve_latex_formatting(markdown_file, output_dir=None):
    """
    Process markdown file while preserving LaTeX formatting for PDF generation
    """
    print(f"Processing {markdown_file} with advanced LaTeX preservation...")
    
    if output_dir is None:
        output_dir = os.path.dirname(markdown_file) or '.'
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Get file basename without extension
    basename = os.path.basename(markdown_file)
    name_without_ext = os.path.splitext(basename)[0]
    
    # Read the original content
    with open(markdown_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if it has LaTeX formatting
    has_latex_formatting = (
        '\\textcolor' in content or 
        '\\begin{center}' in content or 
        '\\definecolor' in content
    )
    
    # Set PDF output path
    output_pdf = os.path.join(output_dir, f"{name_without_ext}.pdf")
    
    # If it doesn't have LaTeX formatting, add some standard enhancements
    if not has_latex_formatting:
        # Add advanced LaTeX formatting similar to malachi_dunn_template
        # Keep the existing YAML header if there is one
        if content.startswith('---'):
            # Find the end of frontmatter
            frontmatter_end = content.find('---', 3)
            if frontmatter_end > 0:
                yaml_header = content[:frontmatter_end+3]
                main_content = content[frontmatter_end+3:].strip()
                
                # Add custom styling to the YAML header
                yaml_header = yaml_header.rstrip("---")
                yaml_header += """  - \\usepackage{setspace}
  - \\singlespacing
  - \\usepackage{xcolor}
  - \\definecolor{accent}{RGB}{70,130,180}
  - \\renewcommand{\\section}[1]{\\vspace{1em}\\large\\textcolor{accent}{\\textbf{#1}}\\vspace{0.5em}}
---
"""
                # Convert section headers to use LaTeX color
                main_content = re.sub(r'^## (.*?)$', r'## \\textcolor{accent}{\1}', main_content, flags=re.MULTILINE)
                
                # Put it all back together
                content = yaml_header + "\n" + main_content
        
        # Fix common markdown escaping issues for LaTeX
        content = content.replace('\\_', '_')
        content = content.replace('\\&', '&')
    
    # Create a temporary file for processing
    temp_file = os.path.join(output_dir, f"{name_without_ext}_advanced.md")
    with open(temp_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
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
        
        # Run pandoc with explicit options for LaTeX
        command = (
            f"PATH=$PATH:/Library/TeX/texbin "
            f"{pandoc_path} {temp_file} -o {output_pdf} "
            f"--pdf-engine=pdflatex --listings"
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
    finally:
        # Clean up the temporary file
        try:
            os.remove(temp_file)
        except:
            pass

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python advanced_pdf_generator.py <markdown_file> [output_directory]")
        sys.exit(1)
        
    markdown_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(markdown_file):
        print(f"Error: File {markdown_file} not found")
        sys.exit(1)
        
    pdf_file = preserve_latex_formatting(markdown_file, output_dir)
    
    if pdf_file:
        print(f"PDF successfully generated at: {pdf_file}")
        sys.exit(0)
    else:
        print("PDF generation failed")
        sys.exit(1)