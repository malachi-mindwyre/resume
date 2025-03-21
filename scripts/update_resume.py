#!/usr/bin/env python3
import pandas as pd
import argparse
import subprocess
import os
import re
import shutil

def load_keywords(keywords_file):
    """Load and return processed keywords file"""
    keywords_df = pd.read_csv(keywords_file)
    # Filter for high priority and high count (top 20)
    high_priority = keywords_df[(keywords_df['priority'] == 'high')].sort_values('count', ascending=False).head(20)
    return high_priority['keyword'].tolist()

def proper_case(text):
    """Properly capitalize terms"""
    # Dictionary of terms that need specific capitalization
    special_terms = {
        'python': 'Python',
        'r': 'R',
        'sql': 'SQL',
        'mysql': 'MySQL',
        'postgresql': 'PostgreSQL',
        'nosql': 'NoSQL',
        'dynamodb': 'DynamoDB',
        'airflow': 'Airflow',
        'docker': 'Docker',
        'kubernetes': 'Kubernetes',
        'databricks': 'Databricks',
        'tableau': 'Tableau',
        'looker': 'Looker',
        'powerbi': 'PowerBI',
        'gcp': 'GCP',
        'aws': 'AWS',
        'azure': 'Azure',
        'saas': 'SaaS',
        'pandas': 'Pandas',
        'numpy': 'NumPy',
        'scipy': 'SciPy',
        'tensorflow': 'TensorFlow',
        'pytorch': 'PyTorch',
        'matplotlib': 'Matplotlib',
        'seaborn': 'Seaborn',
        'apache': 'Apache',
        'spark': 'Spark',
        'pyspark': 'PySpark',
        'hadoop': 'Hadoop',
        'hive': 'Hive',
        'data': 'Data',
        'cloud': 'Cloud',
        'etl': 'ETL',
        'api': 'API',
        'apis': 'APIs',
        'sas': 'SAS',
        'scala': 'Scala',
        'rds': 'RDS',
        'github': 'GitHub',
        'git': 'Git',
        'javascript': 'JavaScript',
        'java': 'Java',
        'snowflake': 'Snowflake',
        'redshift': 'Redshift',
        'ec2': 'EC2',
        'snowpipe': 'Snowpipe',
        'engineer': 'Engineer',
        'engineering': 'Engineering',
        'scientist': 'Scientist',
    }
    
    # Function to replace whole words only
    def replace_whole_word(match):
        word = match.group(0)
        return special_terms.get(word.lower(), word)
    
    # Pattern for whole words only
    pattern = r'\b(' + '|'.join(re.escape(term) for term in special_terms.keys()) + r')\b'
    
    # Replace with properly capitalized versions
    return re.sub(pattern, replace_whole_word, text, flags=re.IGNORECASE)

def fix_formatting(content):
    """Clean up resume formatting"""
    # First preserve the YAML header and LaTeX header
    yaml_match = re.match(r'(---\n.*?---\n\n)', content, re.DOTALL)
    if yaml_match:
        yaml_header = yaml_match.group(1)
        content_without_yaml = content[len(yaml_header):]
    else:
        yaml_header = ""
        content_without_yaml = content
        
    # Check if there's a LaTeX center environment after the YAML
    latex_header_match = re.match(r'(\\begin\{center\}.*?\\end\{center\}\n\n)', content_without_yaml, re.DOTALL)
    if latex_header_match:
        latex_header = latex_header_match.group(1)
        content_without_headers = content_without_yaml[len(latex_header):]
    else:
        latex_header = ""
        content_without_headers = content_without_yaml
    
    # Remove all existing bold formatting
    content_without_headers = re.sub(r'\*\*', '', content_without_headers)
    
    # Fix capitalization throughout the document
    content_without_headers = proper_case(content_without_headers)
    
    # Fix common capitalization errors - lowercase these words when not at the start of a sentence
    words_to_lowercase = ['data', 'cloud', 'database', 'analytics']
    for word in words_to_lowercase:
        # Only replace if not at start of line or after period and not in job titles
        pattern = r'(?<!\n)(?<!\. )(?<!\n- )(?<!\: )(?<!\n### )(?<!\n## )(?<!\n# )(?<!\*\*)(?<!\()(?<!\")' + word.capitalize()
        content_without_headers = re.sub(pattern, word, content_without_headers, flags=re.IGNORECASE)
    
    # Fix job titles and sections with "Data" that should be capitalized
    content_without_headers = content_without_headers.replace("data Engineer", "Data Engineer")
    content_without_headers = content_without_headers.replace("data Scientist", "Data Scientist")
    content_without_headers = content_without_headers.replace("data Analyst", "Data Analyst")
    content_without_headers = content_without_headers.replace("senior data Engineer", "Senior Data Engineer")
    content_without_headers = content_without_headers.replace("Senior data Engineer", "Senior Data Engineer")
    content_without_headers = content_without_headers.replace("lead data Engineer", "Lead Data Engineer")
    content_without_headers = content_without_headers.replace("Lead data Engineer", "Lead Data Engineer")
    content_without_headers = content_without_headers.replace("senior data Analyst", "Senior Data Analyst")
    content_without_headers = content_without_headers.replace("Senior data Analyst", "Senior Data Analyst")
    content_without_headers = content_without_headers.replace("redundant data Engineer", "redundant Data Engineer")
    
    # Fix in profile summary
    content_without_headers = content_without_headers.replace("Accomplished data Engineer", "Accomplished Data Engineer")
    
    # Fix section headings and tool names
    content_without_headers = content_without_headers.replace("Data Engineering Tools", "Data Engineering Tools")
    content_without_headers = content_without_headers.replace("Data Visualization", "Data Visualization")
    content_without_headers = content_without_headers.replace("Big data,", "Big Data,")
    content_without_headers = content_without_headers.replace("databricks", "Databricks")
    
    # Ensure italics formatting for dates and positions
    lines = content_without_headers.split('\n')
    
    for i in range(len(lines)):
        # For job positions and dates
        if ("Contract" in lines[i] or "Full-Time" in lines[i]) and "\\hfill" in lines[i]:
            parts = lines[i].split('\\hfill')
            if len(parts) == 2:
                position_part = parts[0].strip()
                date_part = parts[1].strip()
                
                # Remove any existing asterisks
                position_part = position_part.replace('*', '')
                date_part = date_part.replace('*', '')
                
                # Add proper italics formatting
                position_part = f"*{position_part}*"
                date_part = f"*{date_part}*"
                
                lines[i] = f"{position_part} \\hfill {date_part}"
        
        # For project dates
        if lines[i].startswith('*') and not lines[i].startswith('**') and not lines[i].startswith('- '):
            # This is likely a date in italics
            lines[i] = f"*{lines[i].strip('*')}*"
    
    content_without_headers = '\n'.join(lines)
    
    # Make section titles bold in a clean way (only for Technical Skills section)
    lines = content_without_headers.split('\n')
    in_tech_skills = False
    
    for i in range(len(lines)):
        # Detect Technical Skills section
        if "## Technical Skills" in lines[i]:
            in_tech_skills = True
            continue
        elif lines[i].startswith("##"):
            in_tech_skills = False
            continue
            
        # Only bold category headers in Technical Skills section
        if in_tech_skills and ': ' in lines[i] and not lines[i].startswith('-'):
            parts = lines[i].split(': ', 1)
            lines[i] = f"**{parts[0]}**: {parts[1]}"
    
    content_without_headers = '\n'.join(lines)
    
    # Add URLs for companies
    company_urls = {
        "CopperWyre": "https://copperwyre.com",
        "Disney": "https://disney.com",
        "Pinterest": "https://pinterest.com",
        "Kochava": "https://kochava.com",
    }
    
    # Replace company names with hyperlinks
    for company, url in company_urls.items():
        pattern = fr'{company} \| '
        replacement = fr'[{company}]({url}) \| '
        content_without_headers = re.sub(pattern, replacement, content_without_headers)
    
    # Fix italics in job titles and dates
    content_without_headers = re.sub(r'\*([^*]+?)\* \\hfill \*([^*]+?)\*', r'*\1* \\hfill *\2*', content_without_headers)
    
    # Reconstruct the full content
    return yaml_header + latex_header + content_without_headers

def highlight_keywords(resume_file, output_file, keywords):
    """Process resume without adding keyword emphasis"""
    with open(resume_file, 'r') as f:
        content = f.read()
    
    # Clean up formatting without adding bold to keywords
    processed_content = fix_formatting(content)
    
    # Fix italics with LaTeX for proper PDF rendering
    # Replace markdown italics with LaTeX \textit for positions and dates with \hfill
    processed_content = re.sub(
        r'\*([^*\n]+?)\* \\hfill \*([^*\n]+?)\*',
        r'\\textit{\1} \\hfill \\textit{\2}',
        processed_content
    )
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w') as f:
        f.write(processed_content)
    
    print(f"Updated resume saved to {output_file}")
    return processed_content

def generate_pdf(markdown_file, output_dir="pdf"):
    """Generate PDF from markdown file using pandoc"""
    basename = os.path.basename(markdown_file)
    name_without_ext = os.path.splitext(basename)[0]
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Set PDF output path
    output_pdf = os.path.join(output_dir, f"{name_without_ext}.pdf")
    
    try:
        # Check for pandoc in various locations
        pandoc_paths = [
            "pandoc",                                      # System path
            "/usr/local/bin/pandoc",                       # Standard install location
            "/opt/homebrew/bin/pandoc",                    # Homebrew on Apple Silicon
            "/opt/homebrew/Cellar/pandoc/3.6.4/bin/pandoc" # Specific Homebrew version
        ]
        
        pandoc_found = False
        pandoc_cmd = None
        
        for path in pandoc_paths:
            try:
                # Check if pandoc executable exists and is accessible
                result = subprocess.run(f"which {path}", shell=True, capture_output=True, text=True)
                if result.returncode == 0 and result.stdout.strip():
                    pandoc_found = True
                    pandoc_cmd = path
                    break
            except:
                continue
        
        if not pandoc_found:
            print("Pandoc not found in standard locations. Checking if it's available in PATH...")
            result = subprocess.run("which pandoc", shell=True, capture_output=True, text=True)
            if result.returncode == 0 and result.stdout.strip():
                pandoc_found = True
                pandoc_cmd = "pandoc"
        
        if pandoc_found:
            print(f"Using pandoc at: {pandoc_cmd}")
            # Run pandoc command with pdflatex engine explicitly specified and include the path to pdflatex
            subprocess.run(f"PATH=$PATH:/Library/TeX/texbin {pandoc_cmd} {markdown_file} -o {output_pdf} --pdf-engine=pdflatex", shell=True, check=True)
            
            if os.path.exists(output_pdf):
                print(f"PDF successfully generated: {output_pdf}")
                return output_pdf
            else:
                print(f"PDF generation failed: Output file {output_pdf} not created")
        else:
            print("Pandoc not found. Please install pandoc or add it to your PATH.")
            print("You can install it with: brew install pandoc (macOS) or apt-get install pandoc (Ubuntu)")
            return None
    except subprocess.CalledProcessError as e:
        print(f"PDF generation failed: {e}")
        print("Please check if pandoc is installed correctly")
        return None
    except Exception as e:
        print(f"Error during PDF generation: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description='Update resume with keywords and generate PDF')
    parser.add_argument('--resume', default='templates/resume.md', help='Input resume markdown file')
    parser.add_argument('--keywords', default='data/output/processed_keywords.csv', help='Processed keywords CSV file')
    parser.add_argument('--output', help='Output resume file (default: same as input)')
    parser.add_argument('--pdf', action='store_true', help='Generate PDF after updating')
    parser.add_argument('--pdf-dir', default='data/output', help='Directory for PDF output')
    
    args = parser.parse_args()
    
    # Process keywords if needed
    if not os.path.exists(args.keywords):
        print("Keywords file not found. Running keywords_processor.py...")
        subprocess.run(['python3', 'keywords_processor.py'], check=True)
    
    # Load keywords
    keywords = load_keywords(args.keywords)
    
    # Set output file
    output_file = args.output if args.output else args.resume
    
    # Ensure directories exist
    os.makedirs(os.path.dirname(args.resume), exist_ok=True)
    
    # Update resume
    highlight_keywords(args.resume, output_file, keywords)
    
    # Generate PDF automatically
    pdf_path = generate_pdf(output_file, args.pdf_dir)
    
    if pdf_path:
        print(f"Resume PDF available at: {pdf_path}")
    else:
        print("PDF generation failed. Please manually create the PDF using VS Code with Markdown PDF extension.")

if __name__ == "__main__":
    main()