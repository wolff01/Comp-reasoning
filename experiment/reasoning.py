import csv
import re

def is_deductive_reasoning(response):
    """
    Checks if a response is related to deductive reasoning.
    """
    keywords = [
        "therefore", "hence", "thus", "if", "then", "must be", "logically follows",
        "consequently", "implies", "deduce", "conclusion", "premise"
    ]
    
    if any(keyword in response.lower() for keyword in keywords):
        return True
    
    if "if" in response.lower() and "then" in response.lower():
        return True
    
    return False

def track_deductive_responses(csv_file):
    """
    Reads responses from a CSV file and tracks deductive reasoning instances.
    """
    deductive_count = 0
    
    with open(csv_file, newline='', encoding='utf-8') as file:
        if csv_file == "gpt.csv":
            llm = "ChatGPT"
        if csv_file == "gemini.csv":
            llm = "Gemini"
        if csv_file == "claude.csv":
            llm = "Claude"
        reader = csv.reader(file)
        for i, row in enumerate(reader):
            response = row[4]
            if is_deductive_reasoning(response):
                deductive_count += 1
    
    print(f"Total deductive reasoning responses detected for {llm}: {deductive_count}")
track_deductive_responses("claude.csv")
track_deductive_responses("gpt.csv")
track_deductive_responses("gemini.csv")
