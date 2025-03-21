# Resume Keywords and Formatting Tool

This tool helps you maintain a keyword-optimized resume by analyzing job descriptions, extracting relevant keywords, and enabling quick resume updates.

## Components

1. **keywords_processor.py** - Processes raw keyword data from job listings and preserves multi-word terms
2. **update_resume.py** - Updates your resume with relevant keywords and generates PDF
3. **easy_resume_processor.py** - Single script that runs the entire process (recommended)
4. **update_all.sh** - Simple shell script to run the entire process
5. **resume_formatter.md** - Guide for formatting your resume correctly

## Directory Structure

- **markdown/** - Contains your resume markdown files
- **pdf/** - Contains generated PDF files
- **lead_gen.csv** - Raw keyword data from job listings
- **processed_keywords.csv** - Cleaned and counted keywords

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

## Usage

### Easiest Method: Using the All-in-One Script

Run the entire process with a single command:

```bash
python3 easy_resume_processor.py
```

This script:
- Processes keywords from lead_gen.csv
- Updates your resume with top keywords
- Generates PDF in the pdf/ directory
- Provides detailed logging

### Alternative: Shell Script

Run the shell script for a simpler process:

```bash
./update_all.sh
```

### Advanced: Individual Scripts

If you prefer to run the scripts individually:

#### Process Keywords

```bash
python3 keywords_processor.py
```

#### Update Resume with Keywords

```bash
python3 update_resume.py --resume markdown/resume.md --pdf
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

1. Add job description keywords to `lead_gen.csv`
2. Run `python3 easy_resume_processor.py`
3. Your updated resume will be in:
   - Markdown: `markdown/resume.md`
   - PDF: `pdf/resume.pdf`