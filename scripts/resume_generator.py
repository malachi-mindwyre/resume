#!/usr/bin/env python3
"""
Resume Generator

This script generates a resume structure based on a YAML configuration file.
It creates a new markdown file with sections ordered according to your preferences.
"""

import os
import argparse
import yaml
import sys
import re
from collections import OrderedDict

# Default section content - these would typically come from separate content files
DEFAULT_SECTIONS = {
    "profile": """- Accomplished Data Engineer proficient in Python, SQL, Airflow, Spark, and Scala, including building ETL pipelines predominantly in a GCP cloud environment.
- Solid proficiency in data modeling, database architecture, and utilization of cloud-based data solutions and back-end systems for distributed data processing.
- Expert in streaming services, advertising, mobile apps, and web-scale architecture, with extensive experience working with REST APIs in batch and real-time processing of data.
- Skilled in designing and executing scalable, data-driven solutions using AI, ML, and cloud infrastructure.
- Specialized in predictive analytics, time-series data, and utilization of ML models in MMM, MTA, and other marketing and advertising strategies, leveraging these skills to drive data-driven decision-making and optimization strategies.
- Effective collaborator within agile environments and SDLC, utilizing interpersonal skills to reach alignment among various teams with differing priorities, to ensure steady progress even within tight deadlines.""",
    
    "education": """Georgia Institute of Technology | Masters, Analytics \\hfill Atlanta, GA (In Progress)

Lewis‐Clark State College | Bachelors, Mathematics \\hfill Lewiston, ID | GPA: 3.700/4.0""",
    
    "certifications": """- Data Engineering, Big Data, and Machine Learning on GCP Specialization
- AWS Cloud DevOps Certification
- AWS Certified Machine Learning""",
    
    "skills": """**Languages**: Python, R, Scala, SAS, Matlab  
**Databases**: Snowflake, Redshift, PostgreSQL, MySQL, NoSQL, DynamoDB, Aurora, RDS  
**Data Engineering Tools**: Airflow, dbt, Git, GitHub, Snowpipe, Docker, Kubernetes, Databricks  
**Data Visualization**: Tableau, Looker, PowerBI, Matplotlib, Seaborn  
**Cloud and DevOps**: GCP (Google Cloud Platform), AWS (Amazon Web Services), Microsoft Azure, Databricks, Docker, Kubernetes, SageMaker  
**Frameworks and Libraries**: Pandas, NumPy, Sci-kit learn (SciPy), TensorFlow, PyTorch, XGBoost, LightGBM, CatBoost, Matplotlib, Seaborn  
**Big Data Technologies**: Apache Spark, PySpark, Hadoop, Hive, Pig  
**Cloud Services**: Pub/Sub, Datastream, Vertex AI, Google Kubernetes Engine (GKE), Snowpipe, AWS Batch, AWS Data Pipeline, EC2, Kinesis, Elasticache, SageMaker, Docker""",
    
    "experience": """### [CopperWyre](https://copperwyre.com) \\| Senior Data Engineer, Martech \\hfill
*Contract, Remote* \\hfill *Aug. 2024 - Current*

- Performed ETL on user data to send to Experian and Liveramp that allowed advertising partners to target specific users based on different attributes in targeted MMM and MTA ad-campaigns.
- Increased user match-rates to advertising partners for user targeting by restructuring legacy SQL and Python code that optimized internal data collection techniques.
- Developed a comprehensive media mix model that identified potential savings by optimizing channel allocation, maintaining overall sales performance while reducing marketing spend.
- Automated A/B test experiments by creating executable VertexAI / Google Colab notebooks that automated test and control Martech campaign KNN matching for Google PLA feed experiments designed to increase revenue on targeted advertisements.

### [Disney](https://disney.com) \\| Lead Data Engineer, Adtech \\hfill
*6mo. Contract, Remote* \\hfill *Jan. 2024 - Jul. 2024*

- Built revenue-impacting, direct-to-client data pipelines for the entirety of Hulu, Disney+, and GAM ad-logs for vendor reporting, ad-targeting, and maintaining CCPA and GDPR data compliance within internal tables using GCP, Snowflake, Airflow, and Python, enabling real-time campaign performance visibility for enterprise advertisers.
- Optimized data processing architecture through multi-stage Snowflake pipelines (raw → staging → complete) ensuring data integrity while accommodating delayed ingestion from streaming sources.
- Engineered a self-service reporting solution by integrating Habu clean room as a request management system, reducing redundant Data Engineer workload, eliminating duplicate client charges, and increasing advertiser confidence through transparent campaign analytics.

### [Pinterest](https://pinterest.com) \\| Data Analyst, Martech \\hfill
*12mo. Contract, Remote* \\hfill *Jan. 2023 - Jan. 2024*

- Built an automated insights generation system that transformed manual reporting processes into programmatic workflows, reducing analysis time from days to hours for high-value advertisers by leveraging Presto, Spark SQL, and Pandas.
- Conducted sophisticated cohort analysis identifying statistically significant behavior patterns among targeted user segments, enabling advertisers to optimize campaign targeting and increase conversion rates.
- Engineered data pipelines that automatically populated Google Sheets with visualizations and used internal ML tools to generate contextual narratives, dramatically scaling the insights delivery process.
- Led technical investigation identifying causal factors affecting content engagement rates based on upload methodologies, uncovering critical platform optimizations for publisher growth.

### [Kochava](https://kochava.com) \\| Senior Data Analyst, Adtech \\hfill
*Full-Time, Sandpoint, ID* \\hfill *Jan. 2019 - Jan. 2023*

- Developed a proprietary attribution modeling system processing data from $3.5B in annual ad spend, using time-delta analysis to distinguish between organic and ad-driven conversions.
- Created advanced fraud detection algorithms analyzing temporal patterns in user behavior, identifying non-human traffic patterns that would have otherwise inflated campaign performance metrics.
- Engineered a lifetime value calculation framework connecting ad impressions to in-app purchase events, enabling advertisers to optimize campaigns based on true incremental ROI rather than click-through rates.
- Directed incremental lift studies and control group analytics for flagship clients, including TikTok, utilizing advanced data analysis to reveal strategic insights for ad optimization and communicating complex findings to C-suite and non-technical stakeholders, influencing data-driven decision-making.""",
    
    "projects": """### Polling subreddit posts with Airflow, Google Cloud Function, and BigQuery \\hfill
*Jan. 2023*

- Built an automation system that polls a subreddit via REST API, dedupes the posts in a database, and streams the data to a pub/sub topic. I also wrote a consumer client that consumes from the topic and relays updates to its downstream clients.

### Predicting Lichess chess winners with RandomForest and XGBoost \\hfill
*Jan. 2020*

- Predicted chess winner based on a series of first opening moves and associated features, and then determined the best openings to play ‐ which matches current chess literature.

### Interaction factoring and age prediction of drug users in Colorado \\hfill
*Dec. 2019*

- Developed R plots that showed interactions of various narcotics and narcotics found within overdose victims and determined likelihood of death based on demographic group via clustering algorithm.""",
    
    "publications": """App Developer Magazine, "New Lookback Attribution Windows for SAN Networks." \\hfill *Feb. 2022*"""
}

# YAML header template for the resume
YAML_HEADER = """---
geometry: margin=0.5in
output: pdf_document
header-includes:
  - \\usepackage{fancyhdr}
  - \\pagestyle{empty}
  - \\pagenumbering{gobble}
  - \\usepackage{hyperref}
  - \\hypersetup{colorlinks=true, linkcolor=blue, urlcolor=blue}
---
"""

# LaTeX contact info section template
CONTACT_TEMPLATE = """\\begin{center}
\\large\\textbf{${name}}

${title}

\\href{mailto:${email}}{${email}} | ${phone} | ${location}

\\href{https://${linkedin}}{${linkedin}} | \\href{https://${github}}{${github}} | \\href{https://${website}}{${website}}
\\end{center}
"""

def load_config(config_file):
    """Load resume configuration from YAML file"""
    try:
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        return config
    except Exception as e:
        print(f"Error loading configuration: {e}")
        sys.exit(1)

def load_section_content(section_name, content_dir=None):
    """
    Load content for a resume section
    If a content file exists, use it; otherwise use default content
    """
    if content_dir:
        section_file = os.path.join(content_dir, f"{section_name}.md")
        if os.path.exists(section_file):
            with open(section_file, 'r') as f:
                return f.read().strip()
    
    # Use default content if no file exists
    return DEFAULT_SECTIONS.get(section_name, f"Content for {section_name} section")

def generate_resume(config, output_file, content_dir=None, fix_italics=True):
    """Generate resume markdown based on configuration"""
    sections = []
    
    # Add YAML header
    sections.append(YAML_HEADER)
    
    # Add contact information section
    contact_section = CONTACT_TEMPLATE
    for key, value in config['contact'].items():
        contact_section = contact_section.replace(f"${{{key}}}", value)
    contact_section = contact_section.replace("${name}", config['name'])
    contact_section = contact_section.replace("${title}", config['title'])
    sections.append(contact_section)
    
    # Add sections in the specified order
    for section in config['section_order']:
        if config.get('section_visibility', {}).get(section, True):
            title = config.get('section_titles', {}).get(section, section.capitalize())
            content = load_section_content(section, content_dir)
            sections.append(f"## {title}\n\n{content}")
    
    # Combine all sections
    resume_content = '\n\n'.join(sections)
    
    # Fix italics in the resume content if requested
    if fix_italics:
        # First, escape any & characters that might be interpreted as alignment tabs in LaTeX
        resume_content = resume_content.replace(" & ", " \\& ")
        
        # Special case for technical skills section - handle the category names with bold properly
        resume_content = re.sub(
            r'\*\*([^*\n]+?)\*\*',
            r'\\textbf{\1}',
            resume_content
        )
        
        # Replace markdown italics with LaTeX \emph
        # For positions and dates with \hfill
        resume_content = re.sub(
            r'\*([^*\n]+?)\* \\hfill \*([^*\n]+?)\*',
            r'\\emph{\1} \\hfill \\emph{\2}',
            resume_content
        )
        
        # For standalone italics (not near \hfill)
        resume_content = re.sub(
            r'\*([^*\n]+?)\*',
            r'\\emph{\1}',
            resume_content
        )
    
    # Write to output file
    try:
        with open(output_file, 'w') as f:
            f.write(resume_content)
        print(f"Resume generated successfully: {output_file}")
    except Exception as e:
        print(f"Error writing resume: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Generate a resume from configuration")
    parser.add_argument('--config', default='templates/resume_config.yaml', help='Resume configuration file')
    parser.add_argument('--output', default='data/output/resume.md', help='Output resume file')
    parser.add_argument('--content-dir', help='Directory containing section content files')
    parser.add_argument('--no-fix-italics', action='store_true', help='Do not fix italics for LaTeX')
    
    args = parser.parse_args()
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    
    # Load configuration
    config = load_config(args.config)
    
    # Generate resume
    generate_resume(config, args.output, args.content_dir, not args.no_fix_italics)
    
    print("Resume structure generated. You can now process it with update_resume.py to generate a PDF.")

if __name__ == "__main__":
    main()