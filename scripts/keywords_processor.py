import pandas as pd
import string
from collections import Counter
import csv
import re
import os

# Multi-word terms to preserve
PRESERVE_TERMS = [
    "power bi", "decision-making", "dynamo db", "business intelligence", 
    "machine learning", "data engineer", "data engineering", "data scientist",
    "data science", "data modeling", "data pipeline", "data visualization",
    "big data", "rest api", "rest apis", "google cloud", "data warehouse",
    "data lake", "etl pipeline", "etl pipelines", "cloud infrastructure",
    "data solutions", "back-end", "backend", "front-end", "frontend",
    "full-stack", "fullstack", "continuous integration", "continuous deployment",
    "ci/cd", "database management", "database administrator", "data analytics"
]

def process_keywords(input_file, output_file):
    # Load CSV file
    df = pd.read_csv(input_file)
    
    # Regex to match preserved terms (case insensitive)
    preserved_pattern = re.compile(r'\b(' + '|'.join(re.escape(term) for term in PRESERVE_TERMS) + r')\b', 
                                  re.IGNORECASE)
    
    # Function to clean text while preserving special terms
    def extract_keywords(text):
        if pd.isnull(text):
            return []
            
        # Lower-case the text
        text = text.lower()
        
        # Find all preserved terms before removing punctuation
        preserved_matches = preserved_pattern.findall(text)
        
        # Remove punctuation except for hyphens in preserved terms
        text = text.translate(str.maketrans("", "", string.punctuation.replace('-', '')))
        
        # Split on whitespace
        keywords = text.split()
        
        # Add back preserved terms
        keywords.extend(preserved_matches)
        
        return keywords
    
    # Apply cleaning to both columns
    df["high_keywords"] = df["high_priority_keywords"].apply(extract_keywords)
    df["low_keywords"] = df["low_priority_keywords"].apply(extract_keywords)
    
    # Count keywords for high and low priority
    high_counter = Counter()
    low_counter = Counter()
    
    for keywords in df["high_keywords"]:
        high_counter.update(keywords)
    for keywords in df["low_keywords"]:
        low_counter.update(keywords)
    
    # Create dataframes sorted by frequency
    high_df = pd.DataFrame(high_counter.items(), columns=["keyword", "count"]).sort_values(by="count", ascending=False)
    low_df = pd.DataFrame(low_counter.items(), columns=["keyword", "count"]).sort_values(by="count", ascending=False)
    
    # Save to output CSV
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["keyword", "count", "priority"])
        
        # Write high priority keywords
        for _, row in high_df.iterrows():
            writer.writerow([row['keyword'], row['count'], "high"])
            
        # Write low priority keywords
        for _, row in low_df.iterrows():
            writer.writerow([row['keyword'], row['count'], "low"])
    
    print(f"Processed keywords saved to {output_file}")
    
    return high_df, low_df

if __name__ == "__main__":
    high_df, low_df = process_keywords("data/input/lead_gen.csv", "data/output/processed_keywords.csv")
    
    print("High Priority Keywords Count:")
    print(high_df.to_string(index=False))

    print("\nLow Priority Keywords Count:")
    print(low_df.to_string(index=False))