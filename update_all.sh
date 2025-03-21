#!/bin/bash
# Simple Resume Processing Script

echo "===== Starting Resume Processing ====="

# Step 1: Process keywords
echo ""
echo "===== Step 1: Processing keywords ====="
python3 keywords_processor.py

# Step 2: Update resume and generate PDF
echo ""
echo "===== Step 2: Updating resume with keywords ====="
python3 update_resume.py --resume markdown/resume.md

echo ""
echo "===== Resume processing complete! ====="
echo "Your updated resume is available at:"
echo "  - Markdown: markdown/resume.md"
echo "  - PDF: pdf/resume.pdf (if PDF generation was successful)"

# Display the top keywords
echo ""
echo "===== Top 10 keywords used ====="
head -11 processed_keywords.csv | tail -10 | awk -F, '{print NR ". " $1 " (Count: " $2 ")"}'