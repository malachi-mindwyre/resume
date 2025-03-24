#!/bin/bash
# Resume Generator for job-specific optimization

# Make script executable
# chmod +x generate_resume.sh

# Set directory to script location
cd "$(dirname "$0")"

# Initialize variables
BASENAME=""
UPLOAD=false
JOB_TYPE="data_engineer"
TEMPLATE="general"

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
        --job-type)
            JOB_TYPE="$2"
            shift 2
            ;;
        --template)
            TEMPLATE="$2"
            shift 2
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

# Validate job type and template
if [ ! -d "job_types/$JOB_TYPE" ]; then
    echo "Error: Job type '$JOB_TYPE' not found."
    echo "Available job types:"
    find job_types -mindepth 1 -maxdepth 1 -type d | sort | sed 's|job_types/||' | sed 's|^|  - |'
    exit 1
fi

if [ ! -f "job_types/$JOB_TYPE/templates/$TEMPLATE.md" ]; then
    echo "Error: Template '$TEMPLATE' not found for job type '$JOB_TYPE'."
    echo "Available templates for $JOB_TYPE:"
    find "job_types/$JOB_TYPE/templates" -name "*.md" | sort | sed 's|.*/||' | sed 's|\.md$||' | sed 's|^|  - |'
    exit 1
fi

# Run the resume generator
echo "Generating resume for $JOB_TYPE using $TEMPLATE template..."
COMMAND="python3 scripts/resume_generator.py --job-type $JOB_TYPE --template $TEMPLATE --output data/output/resume.md --pdf"

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

# Show the output file paths based on basename
if [ -n "$BASENAME" ]; then
    BASENAME_UNDERSCORE=$(echo "$BASENAME" | tr ' ' '_' | tr '[:upper:]' '[:lower:]')
    echo "Check data/output/${BASENAME_UNDERSCORE}_resume.md and data/output/${BASENAME_UNDERSCORE}_resume.pdf for results."
else
    echo "Check data/output/resume.md and data/output/resume.pdf for results."
fi