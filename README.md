# Interactive Resume Optimizer

[![Python](https://img.shields.io/badge/Python-3.9+-blue)](https://www.python.org)
[![Jupyter](https://img.shields.io/badge/Jupyter-Notebook-orange)](https://jupyter.org/)
[![Pandas](https://img.shields.io/badge/Pandas-green)](https://pandas.pydata.org/)
[![Google Gemini](https://img.shields.io/badge/AI-Google%20Gemini-purple)](https://ai.google.dev/)
[![PDF](https://img.shields.io/badge/PDF-Generation-red)](https://pandoc.org/)

An interactive tool, run via Jupyter Notebook, to optimize your resume for Applicant Tracking Systems (ATS) by analyzing keyword coverage against specific job roles, allowing edits, providing AI suggestions, and generating a polished final resume.

## Overview

This tool helps you tailor your resume by:

1.  **Uploading** your existing resume (PDF, DOCX, or Markdown recommended).
2.  **Selecting** a target job type (e.g., Data Engineer, Software Engineer).
3.  **Analyzing** keyword coverage based on a central, weighted keyword database.
4.  **Displaying** overall coverage, missing keywords, and keyword distribution across sections.
5.  **Providing an interactive editor** to modify resume sections and bullet points (works best with DOCX/MD input).
6.  **Offering AI-powered suggestions** (via Google Gemini) to improve bullet points.
7.  **Allowing** you to apply AI suggestions directly.
8.  **Enabling** section reordering.
9.  **Saving** your edited resume structure as a new custom template for the selected job type.
10. **Generating** the final resume in Markdown and optionally PDF format.
11. **Uploading** the generated PDF to Google Drive (optional).

## Features

*   **Multi-Format Upload:** Accepts `.pdf`, `.docx`, and `.md` resume files. (Note: Structural parsing for interactive editing is most reliable for `.docx` and `.md`).
*   **Job Role Specialization:** Uses `keywords_db.csv` for weighted keywords specific to different roles (e.g., `de`, `se`, `ds`).
*   **Keyword Analysis:** Calculates overall keyword coverage percentage, lists top missing keywords by weight, and shows keyword distribution across parsed sections.
*   **Interactive Editor:** Allows direct editing of parsed resume sections and bullet points within the notebook.
*   **Section Reordering:** Modify the order of resume sections before final generation.
*   **AI Suggestions (Gemini):** Get suggestions for improving bullet points based on content and missing keywords.
*   **Apply Suggestions:** Directly update bullet points with AI-generated suggestions.
*   **Template Management:** Save your edited resume structure as a new custom template for the current job type.
*   **Output Formats:** Generates optimized resume in Markdown (`.md`). Optional PDF generation via Pandoc/LaTeX is included but may fail depending on resume content complexity and local TeX installation; the `.md` file is the primary reliable output. A generic DOCX example output is included in the repository.
*   **Google Drive Integration (Optional):** Upload the final PDF (if successfully generated) to a specified Google Drive folder.

## Project Structure

```
/
├── .env                   # Stores API keys (GITIGNORED)
├── .gitignore             # Specifies intentionally untracked files
├── README.md              # This file
├── requirements.txt       # Python dependencies
├── generate_resume.ipynb  # Main Jupyter Notebook interface
├── keywords_db.csv        # Central database for all keywords
├── data/
│   ├── input/             # Uploaded resumes go here (content GITIGNORED)
│   │   └── .gitkeep
│   └── output/            # Generated resumes saved here (content GITIGNORED)
│       └── .gitkeep
├── job_types/             # Job type-specific resources
│   ├── data_engineer/     # Example: Data Engineer job type
│   │   └── templates/     # Templates for Data Engineers
│   │       └── general.md # Default template
│   ├── data_scientist/    # Example: Data Scientist job type
│   │   └── templates/
│   │       └── general.md
│   └── software_engineer/ # Example: Software Engineer job type
│       └── templates/
│           └── general.md
└── scripts/
    └── resume_generator.py  # Backend Python script with core logic
```

## Setup

1.  **Clone Repository:**
    ```bash
    git clone <your-repo-url>
    cd keywords
    ```

2.  **Create Virtual Environment (Recommended):**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **API Keys & Credentials:**
    *   **Google Gemini API Key (Required for AI Suggestions):**
        *   Obtain an API key from [Google AI Studio](https://aistudio.google.com/app/apikey).
        *   Create a file named `.env` in the project root directory.
        *   Add the following line to `.env`, replacing `YOUR_API_KEY_HERE` with your actual key:
            ```
            GOOGLE_API_KEY='YOUR_API_KEY_HERE'
            ```
        *   The `.gitignore` file is configured to prevent committing this file.
    *   **Google Drive API Credentials (Optional - Only for GDrive Upload):**
        *   Follow Google Cloud instructions to create OAuth 2.0 credentials for the Drive API.
        *   Download the credentials JSON file and save it as `client_secret.json` in the project root.
        *   The first time you use the Google Drive upload feature, you'll be prompted to authenticate via your browser. This will create a `token.pickle` file to store credentials for future runs.
        *   Both `client_secret.json` and `token.pickle` are included in `.gitignore`.

5.  **PDF Generation Dependencies (Optional):**
    *   **Pandoc:** Install Pandoc from [pandoc.org](https://pandoc.org/installing.html). Ensure it's added to your system's PATH.
    *   **LaTeX:** A LaTeX distribution (like TeX Live, MiKTeX, or MacTeX) is required by Pandoc to create PDFs using the default `pdflatex` engine. Install one suitable for your OS and ensure `pdflatex` is in your system's PATH.
    *   **Note:** PDF generation can be sensitive to special characters in the resume content and specific LaTeX configurations. If errors occur (like `Missing \begin{document}`), generating the PDF manually from the output `.md` file using alternative tools (VS Code extensions, other converters) might be necessary.

## Usage

1.  **Launch Jupyter:**
    ```bash
    # Using Jupyter Notebook
    jupyter notebook generate_resume.ipynb

    # Or using Jupyter Lab
    jupyter lab
    ```
    Then open `generate_resume.ipynb`.

2.  **Run the First Cell:** Execute the first code cell in the notebook to load dependencies and set up the UI.

3.  **Use the UI:**
    *   **Upload:** Upload your resume file (DOCX/MD recommended for best editing).
    *   **Configure:** Enter your name, select the target Job Type, and choose a base Template. Decide on Google Drive upload.
    *   **Generate (First Click):** Click the "Generate Resume" button. This parses the resume, displays the Keyword Analysis, and populates the Interactive Editor.
    *   **Edit:** Modify content directly in the Textarea boxes within the editor's Accordion sections.
    *   **Reorder (Optional):** Change the comma-separated list in the "Section Order" box.
    *   **Get AI Suggestions (Optional):** Click the "Suggest" button next to Experience/Project bullet points.
    *   **Apply Suggestions (Optional):** If you like a suggestion, click "Apply Suggestion".
    *   **Save Template (Optional):** Enter a name and click "Save as Template" to save the current editor state.
    *   **Generate (Second Click):** Click "Generate Resume" again. This uses your edits and section order to create the final `.md` file (and attempt PDF generation) in the `data/output/` directory and performs the optional Google Drive upload. A comparison is shown. (A static `.docx` example is also available in `data/output`).

## Customization

*   **Keywords:** Edit `keywords_db.csv` to add/remove/modify keywords, their weights, and associated roles.
*   **Job Types:** Add new subdirectories under `job_types/` for new roles. Each needs a `templates/` subdirectory with at least a `general.md` file. Add the role code (e.g., `pm` for Project Manager) to relevant keywords in `keywords_db.csv`.
*   **Templates:** Add new `.md` template files to the `job_types/{job_type}/templates/` directories. Use the "Save as Template" feature to create templates from your edits.
*   **Capitalization:** Modify the `SPECIAL_TERMS` dictionary in `scripts/resume_generator.py` for custom capitalization rules.

## Troubleshooting

*   **Dependencies:** Ensure all packages in `requirements.txt` are installed in your active environment (`pip install -r requirements.txt`).
*   **PDF Generation Errors:** Verify Pandoc and a LaTeX distribution (with `pdflatex`) are installed and accessible in your system's PATH. Check the error messages from Pandoc in the notebook output. Complex content or specific LaTeX setups might cause failures; consider converting the output `.md` file manually using other tools if needed.
*   **Google Drive Errors:** Ensure `client_secret.json` is present if using the upload feature. Delete `token.pickle` and re-authenticate if token issues occur.
*   **Gemini API Errors:** Check that your `GOOGLE_API_KEY` is correctly set in the `.env` file. Review error messages from the API (e.g., billing issues, content blocking). Check the Google AI Studio dashboard for API status.
*   **PDF Parsing Issues:** Remember that parsing structure from PDFs is unreliable. Use DOCX or MD files for better results with the interactive editor.

## Future Enhancements

*   Implement multi-resume comparison.
*   More advanced template management (e.g., deleting, editing existing).
*   Option to start directly from a template without uploading a resume first.
*   User accounts/profiles for saving preferences.

## License

This project is released under the MIT License.
