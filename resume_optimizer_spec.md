# Resume Optimization System Specification

## Overview
This system helps users optimize their resumes for specific job applications by:
1. Matching their resume to job-specific templates
2. Identifying missing ATS (Applicant Tracking System) keywords
3. Providing guided suggestions for optimization
4. Allowing customization of resume structure
5. Enabling Google Drive integration for saving optimized resumes

## Key Concepts

### Job Type Configuration
- Each job type (e.g., Data Engineer, Data Scientist, etc.) has:
  - **A static keywords file** (e.g., `data_engineer_keywords.csv`) containing curated keywords relevant to that job
  - **One or more templates** (e.g., `data_engineer_template.md`, `data_engineer_pinterest.md`) optimized for that role
- These files are pre-configured and maintained by the administrator
- In the future, users will be able to create and add their own job types and templates

### Resume Templates
- Templates are pre-designed Markdown files with proper formatting
- They include sections and structure optimized for each job type
- Multiple templates may exist for the same job type (e.g., company-specific versions)
- Initial release includes templates focused on Data Engineering positions

## MVP Implementation Plan - Data Engineer Focus

### Phase 1: Core Keyword Analysis and Template Application
1. **Setup and Configuration**
   - Finalize the Data Engineer keyword database (`data_engineer_keywords.csv`)
   - Create a set of Data Engineer templates (general and company-specific)
   - Implement basic keyword matching algorithm

2. **Keyword Processing**
   - Parse job description keywords from job-specific CSV files
   - Categorize keywords by priority (high/low)
   - Generate frequency analysis to identify most important terms
   - Apply special capitalization rules for technical terms

3. **Template Application**
   - Apply job-specific template to resume content
   - Support multiple templates for the same job type
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
   - Provide UI for selecting from multiple job types
   - Support user-created job types and templates

## Workflow Steps

### 1. Job Selection
- User selects from a list of available job types (initially only Data Engineer)
- Each job type is associated with:
  - A set of resume templates (e.g., general, company-specific)
  - A static keyword file with curated ATS keywords
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
- System checks generated resume against job's static keyword file
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
- Parses job-specific keyword files to extract high and low priority keywords
- Performs frequency analysis to identify most important terms
- Generates a processed keywords file for reference

### 2. Template Manager
- Handles multiple resume templates for different job types
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
1. Read keywords from job-specific keyword file
2. Process and prioritize keywords
3. Read resume template from job-specific template directory
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

## Simple File Structure

```
keywords/
├── data/
│   ├── input/                        # User uploads resumes here
│   └── output/                       # Optimized resumes saved here
│       ├── processed_keywords.csv    # Analyzed keywords
│       ├── resume.md                 # Generated resume (Markdown)
│       └── resume.pdf                # Generated resume (PDF)
├── job_types/                        # Job type-specific resources
│   ├── data_engineer/                # Data Engineer job type
│   │   ├── keywords.csv              # Curated keywords for Data Engineers
│   │   └── templates/                # Templates for Data Engineers
│   │       ├── general.md            # Generic Data Engineer template
│   │       ├── pinterest.md          # Pinterest-specific template (local only)
│   │       └── pinterest_alt.md      # Alternative Pinterest template (local only)
│   ├── data_scientist/               # Data Scientist job type (future)
│   │   ├── keywords.csv
│   │   └── templates/
│   │       └── general.md
│   └── ...                           # Other job types
├── scripts/
│   ├── resume_generator.py           # Main processing script
│   └── get_refresh_token.py          # Google Drive authentication helper
├── generate_resume.sh                # Execution script
├── generate_resume.ipynb             # Jupyter interface
└── requirements.txt                  # Python dependencies
```

## Execution Instructions

### Using Jupyter Notebook (Recommended)
1. Ensure all dependencies are installed: `pip install -r requirements.txt`
2. Run `jupyter notebook generate_resume.ipynb`
3. Complete the form (select job type, template, etc.) and click "Generate Resume"

### Using Command Line
```bash
# Generate resume with defaults (Data Engineer, general template)
./generate_resume.sh

# Generate with specific job type and template
./generate_resume.sh --job-type data_engineer --template pinterest --basename "John Doe" --upload
```

### Direct Script Execution
```bash
python3 scripts/resume_generator.py \
    --job-type data_engineer \
    --template general \
    --output data/output/resume.md \
    --pdf
```

## Future Enhancements

1. **User-Created Job Types and Templates**
   - Allow users to create and add their own job types
   - Support custom keyword files and templates
   - Provide a template editor for customization

2. **Natural Language Suggestions**
   - Provide specific guidance for improving resume content
   - Suggest phrasing to incorporate missing keywords naturally

3. **Intelligent Section Organization**
   - Analyze job requirements to determine optimal section order
   - Customize section visibility based on relevance

4. **Multi-format Support**
   - Add support for DOCX, PDF input parsing
   - Generate outputs in multiple formats

5. **Web Interface**
   - Develop a simple web UI for easier interaction
   - Enable drag-and-drop resume uploads

6. **Job-Type Management**
   - Interface for creating, editing, and managing job types
   - Support for importing/exporting job type configurations