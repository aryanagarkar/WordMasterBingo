"""
main.py
-------
Entry point for processing a list of words to fetch definitions and synonyms using the OpenAI API.
Writes results to output files and generates a report using CheckDefinitionsAndSynonyms.
"""

import os
from .meaning_and_synonym_fetcher import get_definitions
from .check_definitions_and_synonyms import CheckDefinitionsAndSynonyms

def main():
    """
    Main workflow:
    1. Reads a list of words from the Resources/WordsToProcess.txt file.
    2. For each word, fetches a definition and three synonyms using OpenAI.
    3. Writes the results to Resources/WordDefinitionsAndSynonyms.txt.
    4. Runs a check and refinement process, writing a report to Resources/SynonymAndDefinitionCheckReport.txt.
    """

    # Determine resource file paths relative to this script
    base_dir = os.path.dirname(os.path.dirname(__file__))
    resources_dir = os.path.join(base_dir, 'Resources')
    words_file_path = os.path.join(resources_dir, 'WordsToProcess.txt')
    output_file_path = os.path.join(resources_dir, 'WordDefinitionsAndSynonyms.txt')
    report_file_path = os.path.join(resources_dir, 'SynonymAndDefinitionCheckReport.txt')

    words = []

    # Read the list of words to process
    try:
        with open(words_file_path, 'r', encoding='utf-8') as reader:
            for line in reader:
                if line.strip():
                    words.append(line.strip())
    except Exception as e:
        print(f"Error reading words file: {e}")
        return

    output_lines = []
    
    # Fetch definitions and synonyms for each word
    for word in words:
        def_and_syns = get_definitions(word)
        if def_and_syns:
            output_lines.append(f"{word}: {def_and_syns}")
        else:
            output_lines.append(f"{word}: (No definition/synonyms found)")

    # Write the results to the output file
    try:
        with open(output_file_path, 'w', encoding='utf-8') as writer:
            for line in output_lines:
                writer.write(line + '\n')
        print(f"Word definitions and synonyms written to: {output_file_path}")
    except Exception as e:
        print(f"Error writing output file: {e}")

    # Run the synonym and definition check, generating a report
    checker = CheckDefinitionsAndSynonyms()
    checker.run_check(output_file_path, report_file_path)

if __name__ == "__main__":
    main() 