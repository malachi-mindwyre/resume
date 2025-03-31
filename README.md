# Resume Keywords Optimizer

A streamlined tool to optimize your resume for ATS systems by analyzing job descriptions and adding relevant keywords. Focused on Data Engineer roles as the MVP.

![Resume Generator](https://img.shields.io/badge/Resume-Generator-blue)
![Python](https://img.shields.io/badge/Python-3.6+-blue)
![Pandas](https://img.shields.io/badge/Pandas-1.0+-green)
![PDF](https://img.shields.io/badge/PDF-Generation-red)

## Overview

This tool helps you create a professionally formatted resume that emphasizes keywords relevant to Data Engineering roles. It:

1. Processes keywords from job listings
2. Identifies which keywords are missing from your resume
3. Adds missing keywords to ensure ATS compatibility
4. Applies job-specific templates to your resume
5. Formats your resume with consistent styling
6. Generates a professional PDF
7. Uploads the PDF to your Google Drive (optional)

## Quick Start

### Option 1: Using Jupyter Notebook (Recommended)

```bash
# Launch Jupyter notebook
jupiter notebook generate_resume.ipynb
```

Then run the notebook and complete the interactive form.

### Option 2: Using the Shell Script

```bash
# Make the script executable
chmod +x generate_resume.sh

# Run the resume generator (without Google Drive upload)
./generate_resume.sh

# Run with Google Drive upload
./generate_resume.sh --upload
```

## Project Structure

```
/
├── data/
│   ├── input/                   # Input files for the generator
│   │   └── keywords.csv         # Curated keywords (moved here)
│   └── output/                  # Optimized resumes saved here
│       ├── processed_keywords.csv # Analyzed keywords 
│       ├── resume.md            # Generated resume (Markdown)
│       └── resume.pdf           # Generated resume (PDF)
├── job_types/                   # Job type-specific resources
│   └── data_engineer/           # Data Engineer job type
│       └── templates/           # Templates for Data Engineers
│           └── general.md       # Generic Data Engineer template
├── scripts/
│   ├── resume_generator.py      # Main Python script
│   └── get_refresh_token.py     # Google Drive authentication helper
├── generate_resume.ipynb        # Jupyter notebook for easy execution
├── generate_resume.sh           # Shell script to run the generator
└── requirements.txt             # Python dependencies
```

## Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/malachi-mindwyre/keywords.git
   cd keywords
   ```

2. Install all dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Install Pandoc (required for PDF generation):
   ```bash
   # macOS
   brew install pandoc
   
   # Ubuntu/Debian
   sudo apt-get install pandoc
   
   # Windows
   choco install pandoc
   ```

4. Make the script executable:
   ```bash
   chmod +x generate_resume.sh
   ```

5. (Optional) For Google Drive upload functionality:
   - Create a Google Cloud Platform project
   - Enable the Google Drive API
   - Create OAuth 2.0 credentials and download as `client_secret.json` (rename it to this exact name)
   - Place the credentials file in the project root
   - Run `python scripts/get_refresh_token.py` to authenticate once

## How It Works

### 1. Job Type Selection

The system is organized by job types (e.g., Data Engineer), each with:
- A curated set of keywords specific to that job
- Templates optimized for that job type
- Specialized formatting guidelines

### 2. Keyword Processing

The system analyzes the keyword file (`data/input/keywords.csv`) to identify:
- **High priority keywords**: Essential terms for the job
- **Low priority keywords**: Secondary terms that add value

Keywords are processed, counted by frequency, and organized for analysis. The results are saved to `data/output/processed_keywords.csv`.

### 3. Template Application

Your resume information is formatted using a template specific to the selected job type:
- `general.md`: Generic template for the job type
- Other company-specific templates available locally

### 4. Keyword Analysis & Integration

The system identifies which keywords from the processed list (`data/output/processed_keywords.csv`) are missing from your resume template and adds them to a dedicated "Keywords" section, ensuring your resume contains relevant terms that ATS systems look for.

### 5. Output Generation

The final resume is generated in both Markdown and PDF formats, with proper formatting for professional presentation. Optional upload to Google Drive is available.

## Customization

### Customize Your Resume

1. Edit the template files in `job_types/data_engineer/templates/` with your personal information
2. Modify the LinkedIn, GitHub, and other links to match your profiles
3. Update your employment history, education, and other sections

### Adding New Job Types

1. Create a new directory under `job_types/` for your job type (e.g., `data_scientist`)
2. Add relevant templates to a `templates` directory within the new job type folder (e.g., `job_types/data_scientist/templates/general.md`). Note: The `keywords.csv` file is now shared and located in `data/input/`. You may need to adjust its contents if adding job types with significantly different keyword requirements.

### Special Capitalization

The script handles special capitalization for technical terms. You can modify these rules in `scripts/resume_generator.py`:

```python
SPECIAL_TERMS = {
    'aws': 'AWS',
    'aws cloud': 'AWS Cloud',
    'aws cloud devops': 'AWS Cloud DevOps',
    'python': 'Python',
    'sql': 'SQL',
    # Add more terms here...
}
```

## Running the Tool

### Option 1: Using the Jupyter Notebook (Recommended)

1. Launch Jupyter:
   ```bash
   jupyter notebook generate_resume.ipynb
   ```

2. Complete the form with your name, template choice, and other options
3. Click "Generate Resume" button

### Option 2: Using the Shell Script

```bash
# Generate resume and PDF with defaults (Data Engineer, general template)
./generate_resume.sh

# Generate resume, PDF, and upload to Google Drive
./generate_resume.sh --upload

# Generate with custom basename and specific template
./generate_resume.sh --job-type data_engineer --template general --basename "John Doe" --upload
```

### Option 3: Running the Python Script Directly

```bash
# Generate resume and PDF
python3 scripts/resume_generator.py \
    --job-type data_engineer \
    --template general \
    --output data/output/resume.md \
    --pdf

# Generate resume, PDF, and upload to Google Drive
python3 scripts/resume_generator.py \
    --job-type data_engineer \
    --template general \
    --output data/output/resume.md \
    --pdf --upload
```

## Troubleshooting

If you encounter any issues:

1. **Make sure all dependencies are installed**:
   ```bash
   pip install -r requirements.txt
   ```

2. **PDF generation issues**:
   - Verify Pandoc installation: `which pandoc`
   - Ensure you have a LaTeX distribution installed (TeX Live or MiKTeX)

3. **Google Drive upload issues**:
   - Check that `client_secret.json` exists in the project root
   - If authentication fails, delete `token.pickle` and try again

## Future Enhancements

- Interactive keyword placement suggestions
- Support for additional job types beyond Data Engineer
- More advanced resume structure customization
- Direct parsing of PDF/DOCX resumes
- Web-based interface

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is released under the MIT License.
