#!/bin/bash
# Simple script to generate resume

# Make script executable
# chmod +x generate_resume.sh

# Set directory to script location
cd "$(dirname "$0")"

# Run the resume generator
python3 scripts/resume_generator.py --input data/input/lead_gen.csv --template templates/resume_template.md --config templates/resume_config.yaml --output data/output/resume.md --pdf

echo "Resume generation complete!"
echo "Check data/output/resume.md and data/output/resume.pdf for results."