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

## Quick Start

```bash
# Make the script executable
chmod +x generate_resume.sh

# Run the resume generator
./generate_resume.sh
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
│   └── resume_generator.py      # Main Python script
├── templates/
│   ├── resume_config.yaml       # Resume structure configuration
│   └── resume_template.md       # Resume template (Markdown)
├── generate_resume.sh           # One-click script to run the generator
└── requirements.txt             # Python dependencies
```

## Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/malachi-mindwyre/resume.git
   cd resume
   ```

2. Install dependencies:
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

### Option 1: Using the Shell Script

```bash
./generate_resume.sh
```

### Option 2: Running the Python Script Directly

```bash
python3 scripts/resume_generator.py \
    --input data/input/lead_gen.csv \
    --template templates/resume_template.md \
    --config templates/resume_config.yaml \
    --output data/output/resume.md \
    --pdf
```

## PDF Generation Troubleshooting

If PDF generation fails:

1. Ensure you have Pandoc installed: `which pandoc`
2. Make sure you have a LaTeX distribution (like TeX Live or MiKTeX)
3. Try an alternative PDF generation method:
   - VS Code with the Markdown PDF extension
   - Online Markdown to PDF converters
   - Alternative Pandoc options: `pandoc resume.md -o resume.pdf --pdf-engine=wkhtmltopdf`

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is released under the MIT License.