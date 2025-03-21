#!/bin/bash
# Simple Resume Processing Script

echo "===== Starting Resume Processing ====="

# Get script directory and base path
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"

# Change to the base directory
cd "$BASE_DIR"

# Step 1: Process keywords
echo ""
echo "===== Step 1: Processing keywords ====="
python3 "$SCRIPT_DIR/keywords_processor.py"

# Step 2: Update resume and generate PDF
echo ""
echo "===== Step 2: Updating resume with keywords ====="
python3 "$SCRIPT_DIR/update_resume.py" --resume templates/resume.md --output data/output/resume.md --pdf-dir data/output

echo ""
echo "===== Resume processing complete! ====="
echo "Your updated resume is available at:"
echo "  - Markdown: data/output/resume.md"
echo "  - PDF: data/output/resume.pdf (if PDF generation was successful)"

# Display the top keywords
echo ""
echo "===== Top 10 keywords used ====="
head -11 data/output/processed_keywords.csv | tail -10 | awk -F, '{print NR ". " $1 " (Count: " $2 ")"}'