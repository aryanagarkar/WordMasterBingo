import os
from .meaning_and_synonym_fetcher import get_definitions
from .check_definitions_and_synonyms import CheckDefinitionsAndSynonyms

def main():
    base_dir = os.path.dirname(os.path.dirname(__file__))
    resources_dir = os.path.join(base_dir, 'Resources')
    words_file_path = os.path.join(resources_dir, 'WordsToProcess.txt')
    output_file_path = os.path.join(resources_dir, 'WordDefinitionsAndSynonyms.txt')
    report_file_path = os.path.join(resources_dir, 'SynonymAndDefinitionCheckReport.txt')

    words = []
    try:
        with open(words_file_path, 'r', encoding='utf-8') as reader:
            for line in reader:
                if line.strip():
                    words.append(line.strip())
    except Exception as e:
        print(f"Error reading words file: {e}")
        return

    output_lines = []
    for word in words:
        def_and_syns = get_definitions(word)
        if def_and_syns:
            output_lines.append(f"{word}: {def_and_syns}")
        else:
            output_lines.append(f"{word}: (No definition/synonyms found)")

    try:
        with open(output_file_path, 'w', encoding='utf-8') as writer:
            for line in output_lines:
                writer.write(line + '\n')
        print(f"Word definitions and synonyms written to: {output_file_path}")
    except Exception as e:
        print(f"Error writing output file: {e}")

    checker = CheckDefinitionsAndSynonyms()
    checker.run_check(output_file_path, report_file_path)

if __name__ == "__main__":
    main() 