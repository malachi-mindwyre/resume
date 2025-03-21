#!/bin/bash
# Simple script to generate resume

# Make script executable
# chmod +x generate_resume.sh

# Set directory to script location
cd "$(dirname "$0")"

# Clear output directory while preserving the directory itself
echo "Clearing output directory..."
mkdir -p data/output
rm -rf data/output/* data/output/.*
# Ensure no hidden files remain (except . and ..)
find data/output -type f -name ".*" -delete

# Run the resume generator
echo "Generating resume..."
python3 scripts/resume_generator.py --input data/input/lead_gen.csv --template templates/resume_template.md --config templates/resume_config.yaml --output data/output/resume.md --pdf

echo "Resume generation complete!"
echo "Check data/output/resume.md and data/output/resume.pdf for results."