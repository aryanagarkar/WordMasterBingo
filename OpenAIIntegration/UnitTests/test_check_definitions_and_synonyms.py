"""
test_check_definitions_and_synonyms.py
-------------------------------------
Unit tests for CheckDefinitionsAndSynonyms. Tests prompt building, refinement logic, and file I/O.
Mocks the OpenAI API call for logic tests and uses temporary files for file I/O.
"""

import os
import tempfile
import pytest
from src.check_definitions_and_synonyms import (
    CheckDefinitionsAndSynonyms,
    GRADE_PROMPT_TEMPLATE,
    SYNONYM_DEF_PROMPT_TEMPLATE,
    WORD_DEF_PROMPT_TEMPLATE,
    SUGGEST_DEF_PROMPT_TEMPLATE,
    SUGGEST_SYNONYM_PROMPT_TEMPLATE,
)

def mock_openai_response_factory(content):
    """
    Returns a mock send_text_completion_request function that always returns the given content in OpenAI response format.
    """

    def mock_send_text_completion_request(prompt):
        """
        Always returns a fixed OpenAI-style response with the provided content, regardless of the prompt.
        """
        
        return '{"choices": [{"message": {"content": "%s"}}]}' % content
    return mock_send_text_completion_request

def test_check_grade_level():
    """
    Test that check_grade_level builds the correct prompt and returns the expected mock response.
    """

    checker = CheckDefinitionsAndSynonyms(send_text_completion_request=mock_openai_response_factory("yes: ok"))
    result = checker.check_grade_level("word", 1, 5)
    assert "yes" in result
    assert "ok" in result
    prompt = GRADE_PROMPT_TEMPLATE.format(synonym="word", min_grade=1, max_grade=5)
    assert "word" in prompt
    assert "1" in prompt and "5" in prompt

def test_check_synonym_matches_definition():
    """
    Test that check_synonym_matches_definition builds the correct prompt and returns the expected mock response.
    """

    checker = CheckDefinitionsAndSynonyms(send_text_completion_request=mock_openai_response_factory("yes: match"))
    result = checker.check_synonym_matches_definition("syn", "def")
    assert "yes" in result
    assert "match" in result
    prompt = SYNONYM_DEF_PROMPT_TEMPLATE.format(synonym="syn", definition="def")
    assert "syn" in prompt and "def" in prompt

def test_check_definition_matches_word():
    """
    Test that check_definition_matches_word builds the correct prompt and returns the expected mock response.
    """

    checker = CheckDefinitionsAndSynonyms(send_text_completion_request=mock_openai_response_factory("yes: match"))
    result = checker.check_definition_matches_word("word", "def")
    assert "yes" in result
    assert "match" in result
    prompt = WORD_DEF_PROMPT_TEMPLATE.format(word="word", definition="def")
    assert "word" in prompt and "def" in prompt

def test_refine_definition_success():
    """
    Test that refine_definition returns the initial definition if the check passes on the first try.
    """

    def mock_call(prompt):
        """
        Returns 'yes: good' for checks, and 'improved definition' if a suggestion is requested.
        """
        
        if "Suggest a better" in prompt:
            return "improved definition"
        return "yes: good"
    checker = CheckDefinitionsAndSynonyms(send_text_completion_request=lambda prompt: '{"choices": [{"message": {"content": "yes: good"}}]}')
    checker.call_openai = mock_call
    result = checker.refine_definition("word", "def", 2)
    assert result == "def"

def test_refine_definition_improves():
    """
    Test that refine_definition returns an improved definition if the initial check fails.
    """

    responses = iter(["no", "improved definition", "yes: good"])
    def mock_call(prompt):
        """
        Returns a sequence of responses to simulate refinement: first 'no', then 'improved definition', then 'yes: good'.
        """
        
        return next(responses)
    checker = CheckDefinitionsAndSynonyms(send_text_completion_request=lambda prompt: "")
    checker.call_openai = mock_call
    result = checker.refine_definition("word", "def", 2)
    assert result == "improved definition"

def test_refine_synonym_success():
    """
    Test that refine_synonym returns the initial synonym if the checks pass on the first try.
    """

    def mock_call(prompt):
        """
        Always returns 'yes: good' to simulate passing all checks.
        """
        
        return "yes: good"
    checker = CheckDefinitionsAndSynonyms(send_text_completion_request=lambda prompt: "")
    checker.call_openai = mock_call
    result = checker.refine_synonym("word", "def", "syn", 1, 5, 2)
    assert result == "syn"

def test_refine_synonym_improves():
    """
    Test that refine_synonym returns the improved synonym if the initial checks fail, and tracks both before and after values.
    """

    responses = iter(["no", "no", "yes: good"])
    prompts = []
    def mock_call(prompt):
        """
        Tracks all prompts and returns a sequence of responses to simulate refinement logic.
        After the sequence, always returns 'yes: good'.
        """
        
        prompts.append(prompt)
        try:
            return next(responses)
        except StopIteration:
            return "yes: good"
    checker = CheckDefinitionsAndSynonyms(send_text_completion_request=lambda prompt: "")
    checker.call_openai = mock_call
    result = checker.refine_synonym("word", "def", "syn", 1, 5, 3)
    assert result == "yes: good"
    assert any("syn" in p for p in prompts)
    assert any("yes: good" in p for p in prompts)

def test_write_report_to_file_and_improved_words_file(monkeypatch):
    """
    Test that write_report_to_file and write_improved_words_file correctly write the expected content to files.
    Uses temporary files to avoid side effects.
    """
    
    checker = CheckDefinitionsAndSynonyms(send_text_completion_request=mock_openai_response_factory("yes"))
    report = ["line1", "line2"]
    lines = ["improved1", "improved2"]
    with tempfile.NamedTemporaryFile(delete=False) as tmp_report, tempfile.NamedTemporaryFile(delete=False) as tmp_words:
        report_path = tmp_report.name
        words_path = tmp_words.name
    try:
        checker.write_report_to_file(report, report_path)
        with open(report_path, "r") as f:
            content = f.read()
            assert "line1" in content and "line2" in content
        checker.write_improved_words_file(lines, words_path)
        with open(words_path, "r") as f:
            content = f.read()
            assert "improved1" in content and "improved2" in content
    finally:
        os.remove(report_path)
        os.remove(words_path) 