#!/bin/bash
# Simple script to generate resume

# Make script executable
# chmod +x generate_resume.sh

# Set directory to script location
cd "$(dirname "$0")"

# Initialize variables
BASENAME=""
UPLOAD=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        --basename)
            BASENAME="$2"
            shift 2
            ;;
        --upload)
            UPLOAD=true
            shift
            ;;
        *)
            shift
            ;;
    esac
done

# Clear output directory while preserving the directory itself
echo "Clearing output directory..."
mkdir -p data/output
rm -rf data/output/* data/output/.*
# Ensure no hidden files remain (except . and ..)
find data/output -type f -name ".*" -delete

# Run the resume generator
echo "Generating resume..."
COMMAND="python3 scripts/resume_generator.py --input data/input/lead_gen.csv --template templates/resume_template.md --config templates/resume_config.yaml --output data/output/resume.md --pdf"

# Add basename parameter if provided
if [ -n "$BASENAME" ]; then
    COMMAND="$COMMAND --basename \"$BASENAME\""
    echo "Using basename: $BASENAME"
fi

# Add upload parameter if enabled
if [ "$UPLOAD" = true ]; then
    COMMAND="$COMMAND --upload"
    echo "Will upload PDF to Google Drive"
fi

# Execute the command
eval $COMMAND

echo "Resume generation complete!"

# Show the output file paths based on basename
if [ -n "$BASENAME" ]; then
    BASENAME_UNDERSCORE=$(echo "$BASENAME" | tr ' ' '_' | tr '[:upper:]' '[:lower:]')
    echo "Check data/output/${BASENAME_UNDERSCORE}_resume.md and data/output/${BASENAME_UNDERSCORE}_resume.pdf for results."
else
    echo "Check data/output/resume.md and data/output/resume.pdf for results."
fi