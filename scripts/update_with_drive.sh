#!/bin/bash
# Resume Processing with Google Drive Integration

echo "===== Starting Resume Processing with Google Drive Integration ====="

# Get script directory and base path
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"

# Change to the base directory
cd "$BASE_DIR"

# Check if credentials.json exists
if [ ! -f "credentials.json" ]; then
    echo ""
    echo "⚠️  credentials.json not found. Copying template..."
    cp "$BASE_DIR/templates/credentials.json.template" "$BASE_DIR/credentials.json"
    echo ""
    echo "⚠️  Please edit credentials.json with your Google API credentials before continuing."
    echo "    For setup instructions, see templates/google_drive_setup.md"
    exit 1
fi

# Step 1: Download from Google Drive
echo ""
echo "===== Step 1: Downloading from Google Sheet ====="
python3 "$SCRIPT_DIR/google_drive_handler.py" --download
if [ $? -ne 0 ]; then
    echo "⚠️  Google Sheet download failed. Using existing file if available."
fi

# Step 2: Process keywords
echo ""
echo "===== Step 2: Processing keywords ====="
python3 "$SCRIPT_DIR/keywords_processor.py"

# Step 3: Update resume and generate PDF
echo ""
echo "===== Step 3: Updating resume with keywords ====="
python3 "$SCRIPT_DIR/update_resume.py" --resume templates/resume.md --output data/output/resume.md --pdf-dir data/output

# Step 4: Upload to Google Drive
echo ""
echo "===== Step 4: Uploading PDF to Google Drive ====="
python3 "$SCRIPT_DIR/google_drive_handler.py" --upload

echo ""
echo "===== Resume processing complete! ====="
echo "Your updated resume is available at:"
echo "  - Markdown: data/output/resume.md"
echo "  - PDF: data/output/resume.pdf (if PDF generation was successful)"

# Display the top keywords
echo ""
echo "===== Top 10 keywords used ====="
head -11 data/output/processed_keywords.csv | tail -10 | awk -F, '{print NR ". " $1 " (Count: " $2 ")"}'