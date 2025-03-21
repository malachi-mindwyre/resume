# Resume Keywords Optimizer

A streamlined tool to maintain a keyword-optimized resume by analyzing job descriptions and formatting your resume professionally.

![Resume Generator](https://img.shields.io/badge/Resume-Generator-blue)
![Python](https://img.shields.io/badge/Python-3.6+-blue)
![Pandas](https://img.shields.io/badge/Pandas-1.0+-green)
![PDF](https://img.shields.io/badge/PDF-Generation-red)

## Overview

This tool helps you create a professionally formatted resume that emphasizes keywords relevant to your target job market. It:

1. Processes keywords from job listings
2. Applies them to your resume template
3. Formats your resume with consistent styling
4. Generates a professional PDF
5. Uploads the PDF to your Google Drive (optional)

## Quick Start

### Option 1: Using Jupyter Notebook (Recommended)

```bash
# Launch Jupyter notebook
jupyter notebook generate_resume.ipynb
```

Then run the single cell in the notebook.

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
│   ├── input/
│   │   └── lead_gen.csv         # Job description keywords
│   └── output/
│       ├── processed_keywords.csv # Analyzed keywords 
│       ├── resume.md            # Generated resume (Markdown)
│       └── resume.pdf           # Generated resume (PDF)
├── scripts/
│   ├── resume_generator.py      # Main Python script
│   └── get_refresh_token.py     # Google Drive authentication helper
├── templates/
│   ├── resume_config.yaml       # Resume structure configuration
│   └── resume_template.md       # Resume template (Markdown)
├── generate_resume.ipynb        # Jupyter notebook for easy execution
├── generate_resume.sh           # Shell script to run the generator
└── requirements.txt             # Python dependencies
```

## Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/malachi-mindwyre/resume.git
   cd resume
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

## Customization

### Add Your Job Keywords

Edit `data/input/lead_gen.csv` to add job keywords:
- **high_priority_keywords**: Keywords you want to emphasize
- **low_priority_keywords**: Secondary keywords

### Customize Your Resume

1. Edit `templates/resume_template.md` with your personal information
2. Adjust `templates/resume_config.yaml` to configure:
   - Your contact information
   - Section ordering
   - Custom section titles

### Special Capitalization

The script handles special capitalization for technical terms like "AWS Cloud DevOps". You can modify these rules in `scripts/resume_generator.py`:

```python
SPECIAL_TERMS = {
    'aws': 'AWS',
    'aws cloud': 'AWS Cloud',
    'aws cloud devops': 'AWS Cloud DevOps',
    # Add more terms here...
}
```

## Running the Tool

### Option 1: Using the Jupyter Notebook (Recommended)

1. Launch Jupyter:
   ```bash
   jupyter notebook generate_resume.ipynb
   ```

2. Run the cell in the notebook

### Option 2: Using the Shell Script

```bash
# Generate resume and PDF
./generate_resume.sh

# Generate resume, PDF, and upload to Google Drive
./generate_resume.sh --upload

# Generate with custom basename
./generate_resume.sh --basename "John Doe" --upload
```

### Option 3: Running the Python Script Directly

```bash
# Generate resume and PDF
python3 scripts/resume_generator.py \
    --input data/input/lead_gen.csv \
    --template templates/resume_template.md \
    --config templates/resume_config.yaml \
    --output data/output/resume.md \
    --pdf

# Generate resume, PDF, and upload to Google Drive
python3 scripts/resume_generator.py \
    --input data/input/lead_gen.csv \
    --template templates/resume_template.md \
    --config templates/resume_config.yaml \
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

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is released under the MIT License.