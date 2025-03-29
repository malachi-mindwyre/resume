#!/bin/bash
# Direct PDF generation script that preserves LaTeX formatting
# Usage: ./direct_pdf.sh <input-markdown> <output-pdf>

if [ $# -lt 2 ]; then
    echo "Usage: $0 <input-markdown> <output-pdf>"
    exit 1
fi

INPUT=$1
OUTPUT=$2

# Use pandoc directly with proper options to preserve LaTeX
pandoc "$INPUT" -o "$OUTPUT" --pdf-engine=pdflatex

if [ $? -eq 0 ]; then
    echo "PDF successfully generated at: $OUTPUT"
else
    echo "PDF generation failed"
fi