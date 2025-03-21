# Simple Resume Generator

A minimalist resume generation tool that processes job description keywords and formats your resume.

## Overview

This tool does three things:
1. Process keywords from job listings
2. Format your resume markdown file
3. Generate a professional PDF

## Quick Start

```bash
# Process keywords and generate resume
python resume_generator.py --input data/input/lead_gen.csv --template resume_template.md --output data/output/resume.md --pdf
```

## Files

- `resume_generator.py` - Main script to process keywords and generate resume
- `resume_template.md` - Your resume content in markdown format
- `resume_config.yaml` - Configuration for resume structure
- `data/input/lead_gen.csv` - Input file with job description keywords
- `data/output/resume.md` - Generated resume markdown
- `data/output/resume.pdf` - Generated PDF version

## Customization

To customize your resume:
1. Edit `resume_template.md` with your information
2. Update `resume_config.yaml` with your preferences
3. Add keywords to `data/input/lead_gen.csv`

## Special Capitalization

The script includes special handling for terms like "AWS Cloud DevOps" to ensure correct capitalization. If you need to add more terms, you can modify the `SPECIAL_TERMS` dictionary in `resume_generator.py`:

```python
SPECIAL_TERMS = {
    'aws': 'AWS',
    'aws cloud': 'AWS Cloud',
    'aws cloud devops': 'AWS Cloud DevOps',
    # Add more terms here...
}
```

## Requirements

- Python 3.6+
- pandas
- pyyaml
- pandoc (for PDF generation)