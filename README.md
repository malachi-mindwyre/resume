# Resume Keywords and Formatting Tool

This tool helps you maintain a keyword-optimized resume by analyzing job descriptions, extracting relevant keywords, and enabling quick resume updates.

## Components

1. **keywords_processor.py** - Processes raw keyword data from job listings and preserves multi-word terms
2. **update_resume.py** - Updates your resume with relevant keywords and generates PDF
3. **resume_formatter.md** - Guide for formatting your resume correctly
4. **resume_executor.ipynb** - Jupyter notebook that runs the entire process with detailed logging

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

### Jupyter Notebook Executor (Recommended)

The easiest way to run the entire process is using the Jupyter notebook:

```bash
jupyter notebook resume_executor.ipynb
```

This notebook:
- Processes keywords from job descriptions
- Updates your resume with top keywords
- Generates PDFs in the pdf/ directory
- Provides detailed logging throughout the process
- Organizes files into appropriate directories
- Customizable through a simple configuration section

The first time you run it, the notebook will:
1. Create markdown/ and pdf/ directories
2. Copy your existing resume-markdown.md to markdown/resume.md
3. Process the keywords and update the resume
4. Generate PDFs in the pdf/ directory

### Manual Process

If you prefer to run the scripts individually:

#### Process Keywords

```bash
python3 keywords_processor.py
```

#### Update Resume with Keywords

```bash
python3 update_resume.py --resume markdown/resume.md --pdf
```

## PDF Generation

The system can generate a PDF using:

1. **Pandoc** (if installed):
   ```bash
   pandoc markdown/resume.md -o pdf/resume.pdf
   ```

2. **VS Code**: Open the markdown file in VS Code and use the Markdown PDF extension

## Workflow

1. Add job description keywords to `lead_gen.csv`
2. Run the Jupyter notebook `resume_executor.ipynb`
3. Find your updated resume in the markdown/ directory
4. Find your generated PDF in the pdf/ directory