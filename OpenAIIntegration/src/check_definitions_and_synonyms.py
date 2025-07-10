"""
check_definitions_and_synonyms.py
--------------------------------
Provides the CheckDefinitionsAndSynonyms class for validating and refining word definitions and synonyms using the OpenAI API.
Includes helpers for prompt building, response parsing, and file I/O. Designed for easy unit testing and mocking.
"""

import os
import json
import re
from .openai_client import send_text_completion_request as real_send_text_completion_request

GRADE_REFERENCE_1_5 = "words like 'forgiveness', 'upset', and 'disaster' are appropriate for grades 1-5"
GRADE_REFERENCE_6_8 = "'absolution', 'resilient', and 'debacle' are appropriate for grades 6-8"
GRADE_REFERENCE_9_12 = "'obsequious', 'ubiquitous', and 'conundrum' are appropriate for grades 9-12"

GRADE_PROMPT_TEMPLATE = (
    "Is the word '{synonym}' appropriate in terms of vocabulary difficulty for students in grades {min_grade} to {max_grade}, "
    "assuming they are participating in an advanced spelling bee or vocabulary competition? "
    f"For reference, {GRADE_REFERENCE_1_5}; {GRADE_REFERENCE_6_8}; {GRADE_REFERENCE_9_12}. "
    "Ignore social or cultural considerations and focus only on word difficulty. Answer with 'yes' or 'no' and a short explanation."
)

SYNONYM_DEF_PROMPT_TEMPLATE = (
    "Does the word '{synonym}' have the same or very similar meaning as the following definition: '{definition}'? "
    "Answer with 'yes' or 'no' and a short explanation."
)

WORD_DEF_PROMPT_TEMPLATE = (
    "Does the following definition accurately describe the word '{word}'? Definition: '{definition}'. "
    "Answer with 'yes' or 'no' and a short explanation."
)

SUGGEST_DEF_PROMPT_TEMPLATE = (
    "Suggest a better, more accurate definition for the word '{word}'. Only return the definition."
)

SUGGEST_SYNONYM_PROMPT_TEMPLATE = (
    "Suggest a better synonym for the word '{word}' that matches the definition '{definition}' "
    "and is appropriate for students in grades {min_grade}-{max_grade}. Only return the word."
)

class CheckDefinitionsAndSynonyms:
    def __init__(self, send_text_completion_request=real_send_text_completion_request):
        """
        Initialize the checker with a function to call the OpenAI API.
        Args:
            send_text_completion_request (callable): Function to send prompts to OpenAI (can be mocked for testing).
        """

        self.send_text_completion_request = send_text_completion_request

    def run_check(self, input_file_path, output_file_path):
        """
        Main workflow for checking and refining definitions and synonyms:
        1. Reads input file with word: definition, easy, medium, hard per line.
        2. Refines each entry using OpenAI and builds a report.
        3. Writes the report and improved words to output files.
        Args:
            input_file_path (str): Path to the input file.
            output_file_path (str): Path to the report output file.
        """

        if not os.path.exists(input_file_path):
            print(f"Error: Input file not found: {input_file_path}")
            return
        report = []
        improved_word_lines = []
        with open(input_file_path, 'r', encoding='utf-8') as reader:
            for line_number, line in enumerate(reader, 1):
                if not line.strip():
                    continue
                try:
                    parts = line.split(': ', 1)
                    if len(parts) != 2:
                        print(f"Warning: Skipping malformed line {line_number}: {line.strip()}")
                        continue
                    word = parts[0].strip()
                    # Parse definition and synonyms using pipe separator
                    def_and_syns = [x.strip() for x in parts[1].split('|')]
                    if len(def_and_syns) < 4:
                        print(f"Warning: Skipping line {line_number} - insufficient synonyms: {line.strip()}")
                        continue
                    
                    # Refine definition and synonyms using OpenAI
                    definition = self.refine_definition(word, def_and_syns[0], 3, synonyms=def_and_syns[1:4])
                    easy = self.refine_synonym(word, definition, def_and_syns[1], 1, 5, 3)
                    medium = self.refine_synonym(word, definition, def_and_syns[2], 6, 8, 3)
                    hard = self.refine_synonym(word, definition, def_and_syns[3], 9, 12, 3)
                    report_entry = self.generate_report_entry(word, definition, easy, medium, hard)
                    report.append(report_entry)
                    improved_word_lines.append(f"{word}: {definition}|{easy}|{medium}|{hard}")
                except Exception as e:
                    print(f"Error processing line {line_number}: {e}")
        self.write_report_to_file(report, output_file_path)
        improved_words_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Resources', 'WordDefinitionsAndSynonyms_Improved.txt')
        self.write_improved_words_file(improved_word_lines, improved_words_file_path)

    def generate_report_entry(self, word, definition, easy, medium, hard):
        """
        Build a formatted report entry for a word and its synonyms, including checks.
        Args:
            word (str): The word.
            definition (str): The refined definition.
            easy (str): Easy synonym.
            medium (str): Medium synonym.
            hard (str): Hard synonym.
        Returns:
            str: The formatted report entry.
        """

        return (
            f"Word: {word}\n"
            f"  Definition: {definition}\n"
            f"  DefinitionCheck: {self.check_definition_matches_word(word, definition)}\n"
            f"  Easy: {easy} - Grade: {self.check_grade_level(easy, 1, 5)}; DefMatch: {self.check_synonym_matches_definition(easy, definition)}\n"
            f"  Medium: {medium} - Grade: {self.check_grade_level(medium, 6, 8)}; DefMatch: {self.check_synonym_matches_definition(medium, definition)}\n"
            f"  Hard: {hard} - Grade: {self.check_grade_level(hard, 9, 12)}; DefMatch: {self.check_synonym_matches_definition(hard, definition)}\n"
        )

    def write_report_to_file(self, report, output_file_path):
        """
        Write the report entries to a file.
        Args:
            report (list of str): The report entries.
            output_file_path (str): Path to the output file.
        """

        try:
            with open(output_file_path, 'w', encoding='utf-8') as writer:
                for entry in report:
                    writer.write(entry)
                    writer.write("\n")
            print(f"Report written successfully to: {output_file_path}")
        except Exception as e:
            print(f"Error writing to file: {e}")

    def check_grade_level(self, synonym, min_grade, max_grade):
        """
        Check if a synonym is appropriate for a given grade range using OpenAI.
        Args:
            synonym (str): The synonym to check.
            min_grade (int): Minimum grade.
            max_grade (int): Maximum grade.
        Returns:
            str: OpenAI's response.
        """

        prompt = GRADE_PROMPT_TEMPLATE.format(synonym=synonym, min_grade=min_grade, max_grade=max_grade)
        return self.call_openai(prompt)

    def check_synonym_matches_definition(self, synonym, definition):
        """
        Check if a synonym matches a given definition using OpenAI.
        Args:
            synonym (str): The synonym to check.
            definition (str): The definition to match.
        Returns:
            str: OpenAI's response.
        """

        prompt = SYNONYM_DEF_PROMPT_TEMPLATE.format(synonym=synonym, definition=definition)
        return self.call_openai(prompt)

    def check_definition_matches_word(self, word, definition):
        """
        Check if a definition matches a word using OpenAI.
        Args:
            word (str): The word to check.
            definition (str): The definition to match.
        Returns:
            str: OpenAI's response.
        """

        prompt = WORD_DEF_PROMPT_TEMPLATE.format(word=word, definition=definition)
        return self.call_openai(prompt)

    def call_openai(self, prompt):
        """
        Send a prompt to OpenAI and parse the response content.
        Args:
            prompt (str): The prompt to send.
        Returns:
            str: The content from OpenAI's response, or an error message.
        """

        try:
            response = self.send_text_completion_request(prompt)
            if response:
                response_node = json.loads(response)
                content = (
                    response_node.get("choices", [{}])[0]
                    .get("message", {})
                    .get("content", "")
                )
                return content if content else "Error: No content in response"
            else:
                return "Error: No response from OpenAI"
        except Exception as e:
            return f"Error: {e}"

    def has_duplicate_in_definition(self, definition, words_to_check):
        """
        Returns True if any word in words_to_check appears as a whole word (case-insensitive) in the definition.
        """
        for w in words_to_check:
            if not w:
                continue
            pattern = r'\b' + re.escape(w) + r'\b'
            if re.search(pattern, definition, re.IGNORECASE):
                return True
        return False

    def refine_definition(self, word, initial_definition, max_tries, synonyms=None):
        """
        Refine a definition by checking and, if needed, improving it using OpenAI.
        Args:
            word (str): The word being defined.
            initial_definition (str): The initial definition.
            max_tries (int): Maximum number of refinement attempts.
            synonyms (list of str, optional): List of synonyms to check for duplication in the definition.
        Returns:
            str: The refined definition.
        """

        definition = initial_definition
        if synonyms is None:
            synonyms = []
        words_to_check = [word] + synonyms
        for _ in range(max_tries):
            if self.has_duplicate_in_definition(definition, words_to_check):
                prompt = SUGGEST_DEF_PROMPT_TEMPLATE.format(word=word)
                suggestion = self.call_openai(prompt)
                if suggestion and "error" not in suggestion.lower():
                    definition = suggestion.strip()
                    continue
                else:
                    break
            check = self.check_definition_matches_word(word, definition)
            if "yes" in check.lower():
                return definition
            prompt = SUGGEST_DEF_PROMPT_TEMPLATE.format(word=word)
            suggestion = self.call_openai(prompt)
            if suggestion and "error" not in suggestion.lower():
                definition = suggestion.strip()
            else:
                break
        return definition

    def refine_synonym(self, word, definition, initial_synonym, min_grade, max_grade, max_tries):
        """
        Refine a synonym by checking and, if needed, improving it using OpenAI.
        Args:
            word (str): The word being defined.
            definition (str): The definition to match.
            initial_synonym (str): The initial synonym.
            min_grade (int): Minimum grade for appropriateness.
            max_grade (int): Maximum grade for appropriateness.
            max_tries (int): Maximum number of refinement attempts.
        Returns:
            str: The refined synonym.
        """

        synonym = initial_synonym
        for _ in range(max_tries):
            match_check = self.check_synonym_matches_definition(synonym, definition)
            grade_check = self.check_grade_level(synonym, min_grade, max_grade)
            if "yes" in match_check.lower() and "yes" in grade_check.lower():
                return synonym
            prompt = SUGGEST_SYNONYM_PROMPT_TEMPLATE.format(
                word=word, definition=definition, min_grade=min_grade, max_grade=max_grade
            )
            suggestion = self.call_openai(prompt)
            if suggestion and "error" not in suggestion.lower():
                synonym = suggestion.strip()
            else:
                break
        return synonym

    def write_improved_words_file(self, lines, file_path):
        """
        Write the improved word lines to a file.
        Args:
            lines (list of str): Improved word lines.
            file_path (str): Path to the output file.
        """
        
        try:
            with open(file_path, 'w', encoding='utf-8') as writer:
                for line in lines:
                    writer.write(line)
                    writer.write("\n")
            print(f"Improved words file written to: {file_path}")
        except Exception as e:
            print(f"Error writing improved words file: {e}") 

    def run_recursive_check(self, input_file_path, output_file_path, max_passes=3):
        """
        Run the checker multiple times on the improved output until no changes are detected.
        Args:
            input_file_path (str): Path to the initial input file.
            output_file_path (str): Path to the final report output file.
            max_passes (int): Maximum number of refinement passes.
        """
        
        current_input = input_file_path
        improved_file_path = os.path.join(os.path.dirname(input_file_path), 'WordDefinitionsAndSynonyms_Improved.txt')
        
        for pass_num in range(1, max_passes + 1):
            print(f"Starting refinement pass {pass_num}...")
            
            # Run the checker on the current input
            self.run_check(current_input, output_file_path)
            
            # Check if the improved file was created
            if not os.path.exists(improved_file_path):
                print(f"No improved file created in pass {pass_num}. Stopping.")
                break
            
            # Compare current input with improved output to detect changes
            if self._files_are_identical(current_input, improved_file_path):
                print(f"No changes detected in pass {pass_num}. Stopping recursive refinement.")
                break
            
            print(f"Changes detected in pass {pass_num}. Continuing to next pass...")
            
            # Use the improved file as input for the next pass
            current_input = improved_file_path
        
        print(f"Recursive refinement completed after {pass_num} passes.")
    
    def _files_are_identical(self, file1_path, file2_path):
        """
        Compare two files to see if they are identical.
        Args:
            file1_path (str): Path to first file.
            file2_path (str): Path to second file.
        Returns:
            bool: True if files are identical, False otherwise.
        """
        try:
            with open(file1_path, 'r', encoding='utf-8') as f1, open(file2_path, 'r', encoding='utf-8') as f2:
                return f1.read() == f2.read()
        except Exception as e:
            print(f"Error comparing files: {e}")
            return False 