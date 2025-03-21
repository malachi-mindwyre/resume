# Resume Formatting Guide

## Markdown Structure
The resume uses standard Markdown with YAML frontmatter for PDF conversion settings.

### Frontmatter
```yaml
---
title: "Your Name"
geometry: margin=1in
output: pdf_document
header-includes:
  - \usepackage{fancyhdr}
  - \pagestyle{empty}
---
```

### Sections
1. **Header**: Name, title, contact information
2. **Profile Summary**: Bulleted list of key qualifications
3. **Education**: Degrees, institutions, locations, dates
4. **Certifications**: List of relevant certifications
5. **Technical Skills**: Categorized list of skills
6. **Professional Experience**: Work history with bullet points
7. **Projects Experience**: Notable projects with bullet points
8. **Publications**: List of publications (if applicable)

## Keywords Integration
To highlight keywords from the processed list:
- Use **bold text** for high-priority keywords
- When adding new bullet points, prioritize mentioning high-count keywords
- Ensure keywords are used naturally and in context

## PDF Generation
Options for generating PDF from markdown:
1. **VSCode Extension**: Use Markdown PDF extension
   - Open the markdown file in VSCode
   - Click the "Open Preview to the Side" button
   - From the preview, use the export button to generate PDF

2. **Terminal Command**: Use pandoc
   ```bash
   pandoc resume-markdown.md -o resume-markdown.pdf
   ```

## Updating Process
1. Run `python keywords_processor.py` to process keywords
2. Review `processed_keywords.csv` for most frequent keywords
3. Edit `resume-markdown.md` to incorporate relevant keywords
4. Generate PDF using preferred method
5. Review and adjust formatting as needed