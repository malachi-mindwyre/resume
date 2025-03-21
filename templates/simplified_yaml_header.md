---
geometry: margin=0.5in
output: pdf_document
header-includes:
  - \usepackage{fancyhdr}
  - \pagestyle{empty}
  - \pagenumbering{gobble}
  # Remove titlesec dependency to avoid LaTeX errors
  - \usepackage{hyperref}
  - \hypersetup{colorlinks=true, linkcolor=blue, urlcolor=blue}
---

# How to Use This Header

If you're experiencing PDF generation errors with pandoc due to missing LaTeX packages, 
replace the YAML header in your resume markdown file with this simplified version.

1. Open your resume markdown file (`markdown/resume.md`)
2. Replace everything between the `---` markers with this simplified header
3. Save the file and run the processing script again

This simplified header removes the dependency on the `titlesec` package which 
is often missing in default LaTeX installations.