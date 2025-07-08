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
    def mock_send_text_completion_request(prompt):
        # Return a valid OpenAI-like response
        return '{"choices": [{"message": {"content": "%s"}}]}' % content
    return mock_send_text_completion_request

def test_check_grade_level():
    checker = CheckDefinitionsAndSynonyms(send_text_completion_request=mock_openai_response_factory("yes: ok"))
    result = checker.check_grade_level("word", 1, 5)
    assert "yes" in result
    assert "ok" in result
    prompt = GRADE_PROMPT_TEMPLATE.format(synonym="word", min_grade=1, max_grade=5)
    # The prompt is built correctly
    assert "word" in prompt
    assert "1" in prompt and "5" in prompt

def test_check_synonym_matches_definition():
    checker = CheckDefinitionsAndSynonyms(send_text_completion_request=mock_openai_response_factory("yes: match"))
    result = checker.check_synonym_matches_definition("syn", "def")
    assert "yes" in result
    assert "match" in result
    prompt = SYNONYM_DEF_PROMPT_TEMPLATE.format(synonym="syn", definition="def")
    assert "syn" in prompt and "def" in prompt

def test_check_definition_matches_word():
    checker = CheckDefinitionsAndSynonyms(send_text_completion_request=mock_openai_response_factory("yes: match"))
    result = checker.check_definition_matches_word("word", "def")
    assert "yes" in result
    assert "match" in result
    prompt = WORD_DEF_PROMPT_TEMPLATE.format(word="word", definition="def")
    assert "word" in prompt and "def" in prompt

def test_refine_definition_success():
    # Always returns yes
    def mock_call(prompt):
        if "Suggest a better" in prompt:
            return "improved definition"
        return "yes: good"
    checker = CheckDefinitionsAndSynonyms(send_text_completion_request=lambda prompt: '{"choices": [{"message": {"content": "yes: good"}}]}')
    checker.call_openai = mock_call
    result = checker.refine_definition("word", "def", 2)
    assert result == "def"

def test_refine_definition_improves():
    # Returns no first, then yes
    responses = iter(["no", "improved definition", "yes: good"])
    def mock_call(prompt):
        return next(responses)
    checker = CheckDefinitionsAndSynonyms(send_text_completion_request=lambda prompt: "")
    checker.call_openai = mock_call
    result = checker.refine_definition("word", "def", 2)
    assert result == "improved definition"

def test_refine_synonym_success():
    # Always returns yes
    def mock_call(prompt):
        return "yes: good"
    checker = CheckDefinitionsAndSynonyms(send_text_completion_request=lambda prompt: "")
    checker.call_openai = mock_call
    result = checker.refine_synonym("word", "def", "syn", 1, 5, 2)
    assert result == "syn"

def test_refine_synonym_improves():
    # Returns no first, then yes, then always yes
    responses = iter(["no", "no", "yes: good"])
    prompts = []
    def mock_call(prompt):
        prompts.append(prompt)
        try:
            return next(responses)
        except StopIteration:
            return "yes: good"
    checker = CheckDefinitionsAndSynonyms(send_text_completion_request=lambda prompt: "")
    checker.call_openai = mock_call
    result = checker.refine_synonym("word", "def", "syn", 1, 5, 3)
    # Check the final result is the improved value
    assert result == "yes: good"
    # Check that the original synonym was tried first
    assert any("syn" in p for p in prompts)
    # Check that the improved value was also used in a prompt
    assert any("yes: good" in p for p in prompts)

def test_write_report_to_file_and_improved_words_file(monkeypatch):
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