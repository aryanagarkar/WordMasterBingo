import os
import json
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
        self.send_text_completion_request = send_text_completion_request

    def run_check(self, input_file_path, output_file_path):
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
                    def_and_syns = [x.strip() for x in parts[1].split(',')]
                    if len(def_and_syns) < 4:
                        print(f"Warning: Skipping line {line_number} - insufficient synonyms: {line.strip()}")
                        continue
                    definition = self.refine_definition(word, def_and_syns[0], 3)
                    easy = self.refine_synonym(word, definition, def_and_syns[1], 1, 5, 3)
                    medium = self.refine_synonym(word, definition, def_and_syns[2], 6, 8, 3)
                    hard = self.refine_synonym(word, definition, def_and_syns[3], 9, 12, 3)
                    report_entry = self.generate_report_entry(word, definition, easy, medium, hard)
                    report.append(report_entry)
                    improved_word_lines.append(f"{word}: {definition}, {easy}, {medium}, {hard}")
                except Exception as e:
                    print(f"Error processing line {line_number}: {e}")
        self.write_report_to_file(report, output_file_path)
        improved_words_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Resources', 'WordDefinitionsAndSynonyms_Improved.txt')
        self.write_improved_words_file(improved_word_lines, improved_words_file_path)

    def generate_report_entry(self, word, definition, easy, medium, hard):
        return (
            f"Word: {word}\n"
            f"  Definition: {definition}\n"
            f"  DefinitionCheck: {self.check_definition_matches_word(word, definition)}\n"
            f"  Easy: {easy} - Grade: {self.check_grade_level(easy, 1, 5)}; DefMatch: {self.check_synonym_matches_definition(easy, definition)}\n"
            f"  Medium: {medium} - Grade: {self.check_grade_level(medium, 6, 8)}; DefMatch: {self.check_synonym_matches_definition(medium, definition)}\n"
            f"  Hard: {hard} - Grade: {self.check_grade_level(hard, 9, 12)}; DefMatch: {self.check_synonym_matches_definition(hard, definition)}\n"
        )

    def write_report_to_file(self, report, output_file_path):
        try:
            with open(output_file_path, 'w', encoding='utf-8') as writer:
                for entry in report:
                    writer.write(entry)
                    writer.write("\n")
            print(f"Report written successfully to: {output_file_path}")
        except Exception as e:
            print(f"Error writing to file: {e}")

    def check_grade_level(self, synonym, min_grade, max_grade):
        prompt = GRADE_PROMPT_TEMPLATE.format(synonym=synonym, min_grade=min_grade, max_grade=max_grade)
        return self.call_openai(prompt)

    def check_synonym_matches_definition(self, synonym, definition):
        prompt = SYNONYM_DEF_PROMPT_TEMPLATE.format(synonym=synonym, definition=definition)
        return self.call_openai(prompt)

    def check_definition_matches_word(self, word, definition):
        prompt = WORD_DEF_PROMPT_TEMPLATE.format(word=word, definition=definition)
        return self.call_openai(prompt)

    def call_openai(self, prompt):
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

    def refine_definition(self, word, initial_definition, max_tries):
        definition = initial_definition
        for _ in range(max_tries):
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
        try:
            with open(file_path, 'w', encoding='utf-8') as writer:
                for line in lines:
                    writer.write(line)
                    writer.write("\n")
            print(f"Improved words file written to: {file_path}")
        except Exception as e:
            print(f"Error writing improved words file: {e}") 