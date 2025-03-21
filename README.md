# Resume Keywords and Formatting Tool

This tool helps you maintain a keyword-optimized resume by analyzing job descriptions, extracting relevant keywords, and enabling quick resume updates.

## Components

1. **resume_generator.ipynb** - Interactive Jupyter notebook with user-friendly interface (recommended)
2. **scripts/generate_complete_resume.py** - Complete resume generation with configurable section ordering
3. **scripts/resume_generator.py** - Flexible resume structure generator based on YAML configuration
4. **scripts/keywords_processor.py** - Processes raw keyword data from job listings and preserves multi-word terms
5. **scripts/update_resume.py** - Updates resume with relevant keywords and generates PDF
6. **scripts/easy_resume_processor.py** - Simple script that runs the entire process
7. **scripts/easy_resume_processor_with_drive.py** - Process with Google Drive integration
8. **scripts/google_drive_handler.py** - Handles Google Drive operations
9. **scripts/update_all.sh** - Simple shell script to run the entire process

## Directory Structure

- **scripts/** - Contains all processing scripts
- **templates/** - Contains template files and configuration
  - **templates/resume_config.yaml** - Controls resume structure and section ordering
  - **templates/sections/** - Optional directory for individual section content
- **data/input/** - Contains input data (lead_gen.csv)
- **data/output/** - Contains generated output files (processed_keywords.csv, resume.md, resume.pdf)

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Install Pandoc (optional, for PDF generation):
   ```bash
   # macOS
   brew install pandoc
   
   # Ubuntu/Debian
   sudo apt-get install pandoc
   
   # Windows
   choco install pandoc
   ```

   Alternatively, use VS Code with the Markdown PDF extension.

3. For Google Drive integration (optional):
   - Create a Google Cloud project: https://console.cloud.google.com/
   - Enable the Google Drive API
   - Create OAuth credentials (Desktop application)
   - Download credentials and save as `credentials.json` in the project root

## Usage

### Recommended: Using the Interactive Jupyter Notebook

The most user-friendly way to use this tool is through the interactive Jupyter notebook:

```bash
jupyter notebook resume_generator.ipynb
```

This notebook provides:
- An intuitive, visual interface with progress indicators
- Configuration options for customizing the process
- One-click execution of the entire workflow
- Advanced options for running individual steps
- Visual display of processed keywords and results
- Direct links to generated files

### Alternative: Using the All-in-One Script

Run the entire process with a single command:

```bash
python3 scripts/easy_resume_processor.py
```

This script:
- Processes keywords from data/input/lead_gen.csv
- Updates your resume template with top keywords
- Saves the updated resume to data/output/resume.md
- Generates PDF in data/output/resume.pdf
- Provides detailed logging

### Google Drive Integration

To automatically download data from a Google Sheet and upload the PDF to Google Drive:

```bash
python3 scripts/easy_resume_processor_with_drive.py
```

This script:
- Downloads keywords from a Google Sheet to data/input/lead_gen.csv
- Processes keywords and updates the resume
- Generates a PDF
- Uploads the PDF to a specified Google Drive folder
- Provides a direct link to the uploaded PDF

Options:
- `--skip-download`: Skip downloading from Google Sheet
- `--skip-upload`: Skip uploading to Google Drive
- `--sheet-id ID`: Specify a different Google Sheet ID
- `--folder-id ID`: Specify a different Google Drive folder ID

Example with specific Google Drive locations:
```bash
python3 scripts/easy_resume_processor_with_drive.py --sheet-id 1C20hzxMQzT310HSe9DhH8XigArW5VcjAGgQfGafF4o4 --folder-id 1s6n9eS9d2NNy9lyXgoYdPGOwkyGGujnw
```

### Using the Shell Script

Run the shell script for a simpler process without Google Drive integration:

```bash
./scripts/update_all.sh
```

### Advanced: Individual Scripts

If you prefer to run the scripts individually:

#### Process Keywords

```bash
python3 scripts/keywords_processor.py
```

#### Update Resume with Keywords

```bash
python3 scripts/update_resume.py --resume templates/resume.md --output data/output/resume.md --pdf-dir data/output
```

#### Google Drive Operations Only

Download Google Sheet:
```bash
python3 scripts/google_drive_handler.py --download --sheet-id 1C20hzxMQzT310HSe9DhH8XigArW5VcjAGgQfGafF4o4
```

Upload PDF to Google Drive:
```bash
python3 scripts/google_drive_handler.py --upload --folder-id 1s6n9eS9d2NNy9lyXgoYdPGOwkyGGujnw
```

## PDF Generation Troubleshooting

If PDF generation fails with LaTeX errors:

1. Make sure you have a LaTeX distribution installed (like TeX Live or MiKTeX)
2. If you see errors about missing LaTeX packages (like `titlesec.sty`), use the simplified YAML header:
   - Copy the content from `simplified_yaml_header.md` to the top of your resume
   - This removes dependencies on less common LaTeX packages

3. Alternative PDF generation methods:
   - Use VS Code with the Markdown PDF extension
   - Use online Markdown to PDF converters
   - Use `pandoc` with alternative options:
     ```bash
     pandoc markdown/resume.md -o pdf/resume.pdf --pdf-engine=wkhtmltopdf
     ```

## Workflow

### Standard Workflow

1. Add job description keywords to `data/input/lead_gen.csv`
2. Run `python3 scripts/easy_resume_processor.py`
3. Your updated resume will be in:
   - Markdown: `data/output/resume.md`
   - PDF: `data/output/resume.pdf`

### Google Drive Workflow

1. Update your Google Sheet with job description keywords
2. Run `python3 scripts/easy_resume_processor_with_drive.py`
3. Your updated resume will be:
   - Downloaded from Google Sheet
   - Processed and formatted
   - Generated as PDF
   - Uploaded to Google Drive with a shareable link

### Customizing Resume Structure

The resume structure, section ordering, and content can be fully customized:

1. Edit the configuration file:
   ```bash
   nano templates/resume_config.yaml
   ```

2. Change the section ordering in the `section_order` list:
   ```yaml
   section_order:
     - profile
     - skills  # Move skills before education
     - education
     - certifications
     - experience
     - projects
     - publications
   ```

3. Hide sections by setting their visibility to false:
   ```yaml
   section_visibility:
     publications: false  # Hide the publications section
   ```

4. Generate resume with custom structure:
   ```bash
   python3 scripts/generate_complete_resume.py
   ```

For advanced customization, you can create individual section content files in the `templates/sections/` directory, with each file named after the section (e.g., `profile.md`, `skills.md`).