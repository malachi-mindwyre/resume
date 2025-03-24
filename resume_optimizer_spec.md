# Resume Optimization System Specification

## Overview
This system helps users optimize their resumes for specific job applications by:
1. Matching their resume to job-specific templates
2. Identifying missing ATS (Applicant Tracking System) keywords
3. Providing guided suggestions for optimization
4. Allowing customization of resume structure
5. Enabling Google Drive integration for saving optimized resumes

## MVP Implementation Plan - Data Engineer Focus

### Phase 1: Core Keyword Analysis and Template Application
1. **Setup and Configuration**
   - Finalize the Data Engineer keyword database using `lead_gen.csv`
   - Ensure template structure supports variable substitution
   - Implement basic keyword matching algorithm

2. **Keyword Processing**
   - Parse job description keywords from CSV input
   - Categorize keywords by priority (high/low)
   - Generate frequency analysis to identify most important terms
   - Apply special capitalization rules for technical terms

3. **Template Application**
   - Apply job-specific template to resume content
   - Support multiple templates (basic, Pinterest-specific, etc.)
   - Standardize formatting for professional presentation

4. **Keyword Analysis and Integration**
   - Identify missing keywords from the resume
   - Add missing keywords to dedicated "Keywords" section
   - Highlight existing keywords in the resume

5. **Output Generation**
   - Generate Markdown formatted resume
   - Convert to PDF using Pandoc
   - Support uploading to Google Drive (optional)

### Phase 2: Advanced Features (Post-MVP)
1. **Interactive Optimization Suggestions**
   - Provide specific suggestions for keyword placement
   - Implement natural language guidance for content improvement

2. **Structure Customization**
   - Allow section reordering based on job requirements
   - Support conditional sections based on job type

3. **Multi-Job Support**
   - Expand beyond Data Engineer to other job types
   - Create job-specific keyword libraries

## Workflow Steps

### 1. Job Selection
- User selects from a list of available jobs/templates
- Each job is associated with:
  - A resume template (e.g., `resume_template_pin.md` for Pinterest)
  - ATS keyword requirements (from `lead_gen.csv`)
  - Industry-specific formatting guidelines

### 2. Resume Input
- User places their current resume in `/data/input/` or uses an existing template
- System supports templates in Markdown format
- User provides basic information (name, contact details) through the interface

### 3. Template Application
- System applies the selected job template to the user's resume
- Templates include:
  - Standardized sections (Experience, Education, Skills)
  - Job-specific section requirements
  - Recommended content structure

### 4. Keyword Analysis
- System checks generated resume against job's ATS keywords from `lead_gen.csv`
- Analysis identifies:
  - Present keywords (already in the resume)
  - Missing keywords (flagged for addition)
- Keywords are prioritized based on frequency and importance

### 5. Keyword Integration
- System adds missing keywords to a "Keywords" section at the bottom of the resume
- This ensures 100% keyword coverage while maintaining resume quality
- Special terms are properly capitalized (AWS, SQL, etc.)

### 6. Output Generation
- System generates the final resume in Markdown format
- Converts to PDF using Pandoc
- (Optional) Uploads to Google Drive for sharing

## Implementation Components

### 1. Keyword Processor
- Parses `lead_gen.csv` to extract high and low priority keywords
- Performs frequency analysis to identify most important terms
- Generates a processed keywords file for reference

### 2. Template Manager
- Handles multiple resume templates for different jobs
- Applies proper formatting and structure
- Manages special formatting rules (LaTeX headers, etc.)

### 3. Keyword Analyzer
- Compares resume content against required keywords
- Identifies missing terms
- Applies special capitalization rules for technical terms

### 4. Output Generator
- Creates the final Markdown file
- Generates PDF using Pandoc
- Handles Google Drive integration

### 5. User Interface
- Jupyter Notebook interface for interactive use
- Command-line script for automation
- Simple form inputs for customization

## Technical Implementation

### Data Flow
1. Read keywords from `lead_gen.csv`
2. Process and prioritize keywords
3. Read resume template from `/templates/`
4. Apply template and identify missing keywords
5. Generate final resume with keywords
6. Output to Markdown and PDF
7. (Optional) Upload to Google Drive

### Key Algorithms
1. **Keyword Extraction**:
   ```python
   def extract_keywords(text):
       # Convert to lowercase and remove punctuation
       text = text.lower()
       text = re.sub(r'[^\w\s]', ' ', text)
       # Extract individual words and phrases
       keywords = []
       for word in text.split():
           keywords.append(word)
       # Add multi-word phrases
       if len(text.strip()) > 0:
           if len(text.split()) > 1:
               keywords.append(text)
       return keywords
   ```

2. **Keyword Matching**:
   ```python
   def find_unused_keywords(resume_content, keywords_file):
       # Read processed keywords
       df = pd.read_csv(keywords_file)
       # Filter by frequency threshold
       df = df[df['count'] >= min_count]
       # Find missing keywords
       resume_lower = resume_content.lower()
       unused_keywords = []
       for keyword in df['keyword']:
           if keyword.lower() not in resume_lower:
               unused_keywords.append(keyword)
       return unused_keywords
   ```

3. **Template Application**:
   ```python
   def generate_resume(template_file, config_file, output_file, keywords_file):
       # Read template
       with open(template_file, 'r') as f:
           content = f.read()
       # Apply formatting
       content = fix_capitalization(content)
       # Add missing keywords
       unused_keywords = find_unused_keywords(content, keywords_file)
       if unused_keywords:
           # Add to Keywords section
           content += "\n\n## Keywords\n\n"
           content += ", ".join(unused_keywords)
       # Write output
       with open(output_file, 'w') as f:
           f.write(content)
       return content
   ```

## File Structure
```
keywords/
├── data/
│   ├── input/          # User uploads resumes here
│   │   └── lead_gen.csv # Job description keywords
│   └── output/         # Optimized resumes saved here
│       ├── processed_keywords.csv # Analyzed keywords
│       ├── resume.md    # Generated resume (Markdown)
│       └── resume.pdf   # Generated resume (PDF)
├── scripts/
│   ├── resume_generator.py  # Main processing script
│   └── get_refresh_token.py # Google Drive authentication helper
├── templates/
│   ├── resume_template.md       # Base template
│   ├── resume_template_pin.md   # Pinterest-specific template
│   └── resume_template_pin_no_copperwyre.md # Alternative Pinterest template
├── generate_resume.sh           # Execution script
└── generate_resume.ipynb        # Jupyter interface
```

## Execution Instructions

### Using Jupyter Notebook (Recommended)
1. Ensure all dependencies are installed: `pip install -r requirements.txt`
2. Run `jupyter notebook generate_resume.ipynb`
3. Complete the form and click "Generate Resume"

### Using Command Line
```bash
# Generate resume with defaults
./generate_resume.sh

# Generate with custom name and upload to Google Drive
./generate_resume.sh --basename "John Doe" --upload
```

### Direct Script Execution
```bash
python3 scripts/resume_generator.py \
    --input data/input/lead_gen.csv \
    --template templates/resume_template.md \
    --output data/output/resume.md \
    --pdf
```

## Future Enhancements

1. **Natural Language Suggestions**
   - Provide specific guidance for improving resume content
   - Suggest phrasing to incorporate missing keywords naturally

2. **Intelligent Section Organization**
   - Analyze job requirements to determine optimal section order
   - Customize section visibility based on relevance

3. **Multi-format Support**
   - Add support for DOCX, PDF input parsing
   - Generate outputs in multiple formats

4. **Web Interface**
   - Develop a simple web UI for easier interaction
   - Enable drag-and-drop resume uploads

5. **Multiple Job Type Support**
   - Expand beyond Data Engineer to other job types
   - Create job-specific keyword libraries and templates